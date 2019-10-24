import sys
import io
import argparse
import numpy as np
import pickle

####### NOT USED ...?


class TokenizerWrapper():

    def __init__(self, args):
        """
        Tokenizer model loading etc goes here
        """
        from keras.models import load_model
        self.model = load_model(args.model)
        with open(args.vocab,'rb') as inf:
            self.vocab = pickle.load(inf)
        self.args=args
            
    def parse_text(self,txt):
        return tokenizer.tokenize_text(txt,self.model,self.vocab,self.args.sentence_mode)
    
def launch(args,q_in,q_out):
    global tokenizer #imports have to happen within launch() after fork()
    from tokenizer import tokenizer
    
    t=TokenizerWrapper(args)
    while True:
        print("I am tokenizer and I wait for more batches",file=sys.stderr,flush=True)
        jobid,txt=q_in.get()
        if jobid=="FINAL":
            q_out.put((jobid,txt))
            print("Tokenizer exiting",file=sys.stderr, flush=True)
            return
        print("I am tokenizer and I got a batch",file=sys.stderr,flush=True)
        q_out.put((jobid,t.parse_text(txt)))
    
argparser = argparse.ArgumentParser(description='Tokenize text')
argparser.add_argument("--model", default="model", help="model file")
argparser.add_argument("--vocab", default="vocab.pickle", help="vocab file")
argparser.add_argument("--sentence-mode", default=False, action="store_true", help="Input is one sentence per line.")


