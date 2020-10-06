import sys
import io
import argparse
import numpy as np
import pickle

def launch(args,q_in,q_out):
    while True:
        jobid,txt=q_in.get()
        if jobid=="FINAL":
            q_out.put((jobid,txt))
            return
        cache=io.StringIO()
        for line in txt.split("\n"):
            line=line.strip()
            if not line:
                continue
            if line.startswith("###C:"):
                print(line,file=cache)
            else:
                words=line.split()
                for idx,w in enumerate(words):
                    print(idx+1,w,*(["_"]*8),sep="\t",file=cache)
                print(file=cache)
        q_out.put((jobid,cache.getvalue()))
    
argparser = argparse.ArgumentParser(description='Whitespace tokenizer (sentences one per line, words whitespace separated), comments are obeyed')


