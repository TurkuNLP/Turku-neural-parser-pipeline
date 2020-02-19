import subprocess
import os.path
import sys
import hashlib
import io
import http.server
import urllib
import argparse

from .universal_lemmatizer.predict_lemmas import Lemmatizer

class LemmatizerWrapper():

    def __init__(self, args):
        """
        Lemmatizer model loading
        """
        arguments=["-model", args.model, "-gpu", str(args.gpu), "-batch_size", str(args.batch_size), "-fast", "-max_length", str(args.max_length)]
        if args.replace_unk:
            arguments.append("-replace_unk")
        self.lemmatizer_model=Lemmatizer(arguments)
        pass

            
    def parse_text(self,conllu):
        result_conllu=self.lemmatizer_model.lemmatize_batch(conllu)
        return result_conllu

def launch(args,q_in,q_out):

    if args.lemma_cache!="" or args.no_xpos==True:
        sys.exit("ERROR! Calling lemmatizer with outdated parameters, you probably need to update your pipeline configs.\nPlease, download updated models with 'python fetch_models.py treebank_code'\nEXITING")

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
argparser.add_argument('--gpu', type=int, default=0, help='Gpu device id, if -1 use cpu')
argparser.add_argument('--batch_size', type=int, default=100, help='Batch size')
argparser.add_argument('--max_length', type=int, default=50, help='Maximum predicted sequence length')
argparser.add_argument('--replace_unk', action="store_true", default=False, help='Replace unk option in opennmt based lemmatizer')
argparser.add_argument('--lemma_cache', type=str, default='', help='Outdated parameter, DO NOT USE.')
argparser.add_argument('--no_xpos', action="store_true", default=False, help='Outdated parameter, DO NOT USE.')
