
import subprocess
import os.path
import sys
import hashlib
import io
import parser_lib
import http.server
import urllib
import dummy_handler
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "universal-lemmatizer"))
from predict_lemmas import Lemmatizer



class LemmatizerWrapper():

    def __init__(self, args):
        """
        Lemmatizer model loading
        """
        arguments=["-model", args.model, "-gpu", str(args.gpu), "-batch_size", str(args.batch_size), "-lemma_cache", args.lemma_cache]
        if args.replace_unk:
            arguments.append("-replace_unk")
        if args.no_xpos:
            arguments.append("-no_xpos")
        self.lemmatizer_model=Lemmatizer(arguments)
        pass

            
    def parse_text(self,conllu):
        result_conllu=self.lemmatizer_model.lemmatize_batch(conllu)
        return result_conllu

def launch(args,q_in,q_out):
    lemmatizer=LemmatizerWrapper(args)
    while True:
        jobid,txt=q_in.get()
        if jobid=="FINAL":
            q_out.put((jobid,txt))
            print("Lemmatizer exiting",file=sys.stderr,flush=True)
            return
        q_out.put((jobid,lemmatizer.parse_text(txt)))

argparser = argparse.ArgumentParser(description='Lemmatize conllu text')
argparser.add_argument('--model', default='models/lemmatizer.pt', type=str, help='Model')
argparser.add_argument('--gpu', type=int, default=-1, help='Gpu device id, if -1 use cpu')
argparser.add_argument('--batch_size', type=int, default=64, help='Batch size')
argparser.add_argument('--lemma_cache', type=str, default='', help='Lemma cache file')
argparser.add_argument('--replace_unk', action="store_true", default=False, help='Replace unk option in opennmt based lemmatizer')
argparser.add_argument('--no_xpos', action="store_true", default=False, help='Do not pass XPOS for the lemmatizer')
