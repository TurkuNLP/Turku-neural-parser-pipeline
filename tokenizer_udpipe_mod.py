import sys
import io
import argparse
import numpy as np
import pickle
try:
    import ufal.udpipe as udpipe
except:
    print("pip3 install ufal.udpipe",file=sys.stderr)
    raise

class UDPipeTokenizerWrapper():

    def __init__(self, args):
        """
        Tokenizer model loading etc goes here
        """
        self.model = udpipe.Model.load(args.model)
        self.pipeline = udpipe.Pipeline(self.model,"tokenize","none","none","conllu")
            
    def parse_text(self,txt):
        err=udpipe.ProcessingError()
        return self.pipeline.process(txt,err)
    
def launch(args,q_in,q_out):
    t=UDPipeTokenizerWrapper(args)
    while True:
        jobid,txt=q_in.get()
        if jobid=="FINAL":
            q_out.put((jobid,txt))
            return
        q_out.put((jobid,t.parse_text(txt)))
    
argparser = argparse.ArgumentParser(description='UDPipe tokenize text')
argparser.add_argument("--model", default="model", help="model file")
