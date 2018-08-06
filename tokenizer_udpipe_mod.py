import sys
import io
import argparse
import numpy as np
import pickle
import re
try:
    import ufal.udpipe as udpipe
except:
    print("pip3 install ufal.udpipe",file=sys.stderr)
    raise

comment_regex=re.compile("^####?C: ?")

class UDPipeTokenizerWrapper():

    def __init__(self, args):
        """
        Tokenizer model loading etc goes here
        """
        self.model = udpipe.Model.load(args.model)
        if args.presegmented:
            self.pipeline = udpipe.Pipeline(self.model,"tokenizer=presegmented","none","none","conllu")
        else:
            self.pipeline = udpipe.Pipeline(self.model,"tokenize","none","none","conllu")
            
    def parse_text(self,txt):
        err=udpipe.ProcessingError()
        tokenized=""
        current_block=[]
        for line in txt.split("\n"):
            if re.match(comment_regex, line.lstrip()): # comment line
                if current_block:
                    tokenized+=self.pipeline.process("\n".join(current_block),err)
                    current_block=[]
                tokenized+=re.sub(comment_regex, "# ", line.lstrip()+"\n")
                continue
            # normal text line, save to current block to be tokenized
            current_block.append(line)
        if current_block:
            tokenized+=self.pipeline.process("\n".join(current_block),err)
        return tokenized
    
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
argparser.add_argument("--presegmented", default=False, action="store_true", help="Input is already sentence segmented (one sentence per line), run only tokenizer.")
