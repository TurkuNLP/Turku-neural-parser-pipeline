import sys
import io
import argparse
import numpy as np
import pickle

class TokenizerWrapper():

    def __init__(self, args):
        """
        Tokenizer model loading etc goes here
        """
        from keras.models import load_model
        self.model = load_model(args.model)
        with open(args.vocab,'rb') as inf:
            self.vocab = pickle.load(inf)
            
    def parse_text(self,txt):
        return tokenizer.tokenize_text(txt,self.model,self.vocab)
    
def launch(args,q_in,q_out):
    global tokenizer #imports have to happen within launch() after fork()
    from tokenizer import tokenizer
    
    t=TokenizerWrapper(args)
    while True:
        print("I am tokenizer and I wait for more batches",file=sys.stderr,flush=True)
        jobid,txt=q_in.get()
        if jobid=="FINAL":
            return
        print("I am tokenizer and I got a batch",file=sys.stderr,flush=True)
        q_out.put((jobid,t.parse_text(txt)))
    
argparser = argparse.ArgumentParser(description='Tokenize text')
argparser.add_argument("--model", default="model", help="model file")
argparser.add_argument("--vocab", default="vocab.pickle", help="vocab file")

