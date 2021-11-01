import os.path
import sys
import io
import argparse
import traceback
import tarfile
from pathlib import Path
from tempfile import NamedTemporaryFile

from diaparser.parsers import Parser


ID,FORM,LEMMA,UPOS,XPOS,FEAT,HEAD,DEPREL,DEPS,MISC=range(10)

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
            cols=line.split("\t")
            sent.append(cols)
    else:
        if sent:
            yield comment, sent

def conllu2dataset(conllu):
    dset=[]
    all_comments=[]
    all_sentences=[]
    for comments,sent in read_conllu(conllu):
        tokens=[line[FORM] for line in sent if line[ID].isdigit()] #gather only those tokens you really want to parse
        dset.append(tokens)
        all_comments.append(comments)
        all_sentences.append(sent)
    return all_comments,all_sentences,dset

def merge(comments,sent,parser_out_sent):
    i=0
    for row in sent:
        if row[ID].isdigit():
            row[HEAD]=str(parser_out_sent.values[HEAD][i])
            row[DEPREL]=parser_out_sent.values[DEPREL][i]
            i+=1
    if comments:
        result="\n".join(comments)+"\n"
    else:
        result=""
    result+="\n".join("\t".join(row) for row in sent)
    result+="\n\n"
    return result
    

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
            comments,sents,dset=conllu2dataset(txt)
            predicted=parser.predict(dset,batch_size=1000)
            res=[]
            for comm,sent,parser_out in zip(comments,sents,predicted.sentences):
                res.append(merge(comm,sent,parser_out))
            q_out.put((jobid,"".join(res)))
        except:
            traceback.print_exc()
            sys.stderr.flush()
            raise
            
argparser = argparse.ArgumentParser()
argparser.add_argument("--model", type=str, help="The model file")
argparser.add_argument("--device", default=0, type=int, help="CUDA device number; set to -1 for CPU")
argparser.add_argument("--batch_size", default=128, type=int, help="The size of each prediction batch")
argparser.add_argument("--lazy", action="store_true", help="Lazy load dataset")
argparser.add_argument("--raw_text", action="store_true", help="Input raw sentences, one per line in the input file.")
        
        

