import os.path
import sys
import io
import argparse
import traceback
import tarfile
from pathlib import Path
from tempfile import NamedTemporaryFile

from diaparser.parsers import Parser


def read_conllu(txt):
    sent=[]
    comment=[]
    for line in txt.split("\n"):
        line=line.strip()
        if not line: # new sentence
            if sent:
                yield comment,sent
            comment=[]
            sent=[]
        elif line.startswith("#"):
            comment.append(line)
        else: #normal line
            sent.append(line.split("\t"))
    else:
        if sent:
            yield comment, sent

def conllu2dataset(conllu):
    dset=[]
    all_comments=[]
    for comments,sent in read_conllu(conllu):
        tokens=[line[1] for line in sent]
        dset.append(tokens)
        all_comments.append(comments)
    return all_comments,dset

def launch(args, q_in, q_out):
    try:
        parser = Parser.load(args.model)
    except:
        traceback.print_exc()
        sys.stderr.flush()
    while True:
        jobid,txt=q_in.get()
        if jobid=="FINAL":
            q_out.put((jobid,txt))
            return
        try:
            comments,dset=conllu2dataset(txt)
            predicted=parser.predict(dset)
            res=[]
            for comm,sent in zip(comments,predicted.sentences):
                if comm:
                    res.append("\n".join(comm))
                res.append(str(sent))
            q_out.put((jobid,"\n".join(res)))
        except:
            traceback.print_exc()
            sys.stderr.flush()
            
argparser = argparse.ArgumentParser()
argparser.add_argument("--model", type=str, help="The model file")
argparser.add_argument("--device", default=0, type=int, help="CUDA device number; set to -1 for CPU")
argparser.add_argument("--batch_size", default=128, type=int, help="The size of each prediction batch")
argparser.add_argument("--lazy", action="store_true", help="Lazy load dataset")
argparser.add_argument("--raw_text", action="store_true", help="Input raw sentences, one per line in the input file.")
        
        

