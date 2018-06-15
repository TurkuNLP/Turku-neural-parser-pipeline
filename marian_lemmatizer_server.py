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
import os.path
from websocket import create_connection

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "universal-lemmatizer"))
from predict_lemmas import Lemmatizer

import prepare_data
ID,FORM,LEMMA,UPOS,XPOS,FEATS,HEAD,DEPREL,DEPS,MISC=range(10)

import time

class LemmatizerWrapper():

    def __init__(self, args):
        """
        Lemmatizer model loading
        """
        self.proc=subprocess.Popen(args=[args.marian_binary,"-m",args.model,"-v",args.model+".vocab.in",args.model+".vocab.out","-p",args.marian_port,"--mini-batch","256","--maxi-batch","100"])
        time.sleep(2)
        self.cache={}
        if args.lemma_cache:  #form upos xpos feats lemma
            with open(args.lemma_cache) as f:
                for line in f:
                    cols=line.strip().split("\t")
                    self.cache[tuple(*cols[:4])]=cols[5]
        self.local_cache={}
        self.args=args

    def parse_text(self,conllu):
        submitted=set()
        to_submit=[]
        submitted_tokdata=[]
        sents=list(prepare_data.read_conllu(conllu.split("\n")))
        ws = create_connection("ws://localhost:{}/translate".format(self.args.marian_port))
        for comments,sent in sents:
            for cols in sent:
                token_data=(cols[FORM],cols[UPOS],cols[XPOS],cols[FEATS])
                if token_data not in self.cache and token_data not in self.local_cache and token_data not in submitted:
                    lem_in=prepare_data.transform_token(cols)[0]
                    to_submit.append(lem_in)
                    submitted_tokdata.append(token_data)
                    submitted.add(token_data)
        
        ws.send("\n".join(to_submit))
        lemmatized=ws.recv()
        #print("LEMMATIZED",lemmatized,file=sys.stderr,flush=True)
        for token_data,lemma in zip(submitted_tokdata,lemmatized.strip().split("\n")):
            self.local_cache[token_data]=prepare_data.detransform_string(lemma)
        result=[]
        for comments,sent in sents:
            for c in comments:
                result.append(c)
            for cols in sent:
                token_data=(cols[FORM],cols[UPOS],cols[XPOS],cols[FEATS])
                if token_data in self.cache:
                    lemma=self.cache[token_data]
                elif token_data in self.local_cache:
                    lemma=self.local_cache[token_data]
                else:
                    assert False
                cols[LEMMA]=lemma
                result.append("\t".join(cols))
            result.append("")
        result.append("")
        return "\n".join(result)

def launch(args,q_in,q_out):
    lemmatizer=LemmatizerWrapper(args)
    while True:
        jobid,txt=q_in.get()
        if jobid=="FINAL":
            q_out.put((jobid,txt))
            lemmatizer.proc.kill()
            lemmatizer.proc.wait()
            return
        q_out.put((jobid,lemmatizer.parse_text(txt)))

argparser = argparse.ArgumentParser(description='Lemmatize conllu text')
argparser.add_argument('--model', type=str, help='Model (modelname.vocab.in and modelname.vocab.out are assumed as vocabularies)')
argparser.add_argument('--marian-binary', type=str, default=os.path.expanduser("~/marian/build/marian-server"),help='Path to marian-server. Default: ~/marian/build/marian-server')
argparser.add_argument('--marian-port', type=str, default="48267", help='Port on which the marian server will run. Default: %(default)s')
argparser.add_argument('--lemma-cache', type=str, default=None, help='a .tsv file with lemma cache')
                       
            

