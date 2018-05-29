import os
from multiprocessing import Process,Pipe

import tokenizer_server as tok_serv
import parser_server as parse_serv
import lemmatizer_server as lemma_serv

import requests

if __name__=="__main__":
    #Start the servers
    tok_in,pipe_in=Pipe(duplex=False) #receive,send is the order of Pipe()
    tag_in,tok_out=Pipe(duplex=False)
    parse_in,tag_out=Pipe(duplex=False)
    lemma_in,parse_out=Pipe(duplex=False)
    pipe_out,lemma_out=Pipe(duplex=False)
    
    tok_args=tok_serv.argparser.parse_args([])
    tok_process=Process(target=tok_serv.launch,args=(tok_args,tok_in,tok_out))
    tok_process.start()

    tag_args=parse_serv.argparser.parse_args(["--model","models/Finnish-Tagger"])
    tag_process=Process(target=parse_serv.launch,args=(tag_args,tag_in,tag_out))
    tag_process.start()
   
    parse_args=parse_serv.argparser.parse_args(["--model","models/Finnish-Parser", "--process_morpho"])
    parse_process=Process(target=parse_serv.launch,args=(parse_args,parse_in,parse_out))
    parse_process.start()

    lemma_args=lemma_serv.argparser.parse_args(["--model", "models/lemmatizer.pt"])
    lemma_process=Process(target=lemma_serv.launch,args=(lemma_args,lemma_in,lemma_out))
    lemma_process.start()

    while True:
        txt=input("ws-text> ")
        pipe_in.send(txt)
        processed=pipe_out.recv()
        print(processed,end="")
        
