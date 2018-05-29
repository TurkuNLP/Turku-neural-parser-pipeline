import sys
import io
import argparse

class TokenizerWrapper():

    def __init__(self):
        """
        Tokenizer model loading etc goes here
        """
        pass
            
    def parse_text(self,txt):
        """Dummy - replace with something intelligent"""
        buff=io.StringIO()
        for line in txt.split("\n"): #make basic conllu, assume whitespace tokenization
            print("# txt: ",line, file=buff)
            for idx,wrd in enumerate(line.split()):
                print(idx+1,wrd,"_","_","_","_","_","_","_","_",sep="\t",file=buff)
            print(file=buff)
        conllu=buff.getvalue()
        return conllu

def launch(args,q_in,q_out):
    t=TokenizerWrapper()
    while True:
        txt=q_in.get()
        q_out.put(t.parse_text(txt))
    
argparser = argparse.ArgumentParser(description='Tokenize text')
