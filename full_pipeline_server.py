import os
from multiprocessing import Process,Pipe

import tokenizer_server as tok_serv
import parser_server as parse_serv

import requests

if __name__=="__main__":
    #Start the servers
    tok_in,pipe_in=Pipe(duplex=False) #receive,send is the order of Pipe()
    tag_in,tok_out=Pipe(duplex=False)
    parse_in,tag_out=Pipe(duplex=False)
    
    tok_args=tok_serv.argparser.parse_args([])
    tok_process=Process(target=tok_serv.launch,args=(tok_args,tok_in,tok_out))
    tok_process.start()

    tag_args=parse_serv.argparser.parse_args(["--model","/usr/share/ParseBank/TinyFinnish-Stanford-model/Finnish-Tagger"])
    tag_process=Process(target=parse_serv.launch,args=(tag_args,tag_in,tag_out))
    tag_process.start()

    pipe_out=parse_in
    
    # parse_args=parse_serv.argparser.parse_args(["--port","34591","--model","/usr/share/ParseBank/TinyFinnish-Stanford-model/Finnish-Parser"])
    # parse_process=Process(target=parse_serv.launch,args=(parse_args,parse_serv.ParserHTTPDummyHandler))
    # parse_process.start()

    while True:
        txt=input("ws-text> ")
        pipe_in.send(txt)
        processed=pipe_out.recv()
        print(processed,end="")
        
