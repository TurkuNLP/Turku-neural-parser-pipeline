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

        if args.model:
            self.model = load_model(args.model)
        else:
            self.model = load_model('model')
        if args.vocab:
            inf = open(args.vocab,'rb')
        else:
            inf = open('vocab.pickle','rb')
        self.vocab = pickle.load(inf)
        inf.close()
            
    def parse_text(self,txt):
        buff=io.StringIO()
        x = []
        for c in txt.replace('\n',''):
            x.append(c)

        xx = tokenizer.make_data_matrix(x, vocab=self.vocab)
        pred = self.model.predict(xx)
        tokenizer.data_matrix_to_conllu(xx, pred, self.vocab, f=buff)
        
        return buff.getvalue()

def launch(args,q_in,q_out):
    global tf, set_session, clear_session,load_model, tokenizer
    import tensorflow as tf
    from keras.backend.tensorflow_backend import set_session, clear_session
    config = tf.ConfigProto()
    #config.gpu_options.per_process_gpu_memory_fraction = -1
    config.gpu_options.allow_growth = True
    set_session(tf.Session(config=config))
    from keras.models import load_model
    from tokenizer import tokenizer
    
    t=TokenizerWrapper(args)
    while True:
        jobid,txt=q_in.get()
        q_out.put((jobid,t.parse_text(txt)))
    
argparser = argparse.ArgumentParser(description='Tokenize text')
argparser.add_argument("--model", help="model file")
argparser.add_argument("--vocab", help="vocab file")

