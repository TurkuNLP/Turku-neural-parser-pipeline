
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
        self.lemmatizer_model=Lemmatizer(["-model", args.model, "-gpu", str(args.gpu), "-batch_size", str(args.batch_size)])
        pass
            
    def parse_text(self,conllu):
        result_conllu=self.lemmatizer_model.lemmatize_batch(conllu)
        return result_conllu

def launch(args,q_in,q_out):
    lemmatizer=LemmatizerWrapper(args)
    while True:
        txt=q_in.recv()
        q_out.send(lemmatizer.parse_text(txt))

argparser = argparse.ArgumentParser(description='Lemmatize conllu text')
argparser.add_argument('--model', default='models/lemmatizer.pt', type=str, help='Model')
argparser.add_argument('--gpu', type=int, default=-1, help='Gpu device id, if -1 use cpu')
argparser.add_argument('--batch_size', type=int, default=64, help='Batch size')
