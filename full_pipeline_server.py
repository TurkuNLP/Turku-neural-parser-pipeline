import os
from multiprocessing import Process

import tokenizer_server as tok_serv
import parser_server as parse_serv

import requests

if __name__=="__main__":
    #Start the servers
    tok_args=tok_serv.argparser.parse_args(["--port","34589"])
    tok_process=Process(target=tok_serv.launch,args=(tok_args,))
    tok_process.start()

    tag_args=parse_serv.argparser.parse_args(["--port","34590","--model","/usr/share/ParseBank/TinyFinnish-Stanford-model/Finnish-Tagger"])
    tag_process=Process(target=parse_serv.launch,args=(tag_args,parse_serv.TaggerHTTPDummyHandler))
    tag_process.start()

    parse_args=parse_serv.argparser.parse_args(["--port","34591","--model","/usr/share/ParseBank/TinyFinnish-Stanford-model/Finnish-Parser"])
    parse_process=Process(target=parse_serv.launch,args=(parse_args,parse_serv.ParserHTTPDummyHandler))
    parse_process.start()

    while True:
        txt=input("ws-text> ")
        r_tok=requests.post("http://127.0.0.1:34589",data=txt.strip().encode("utf-8"))
        tokenized=r_tok.text
        r_tag=requests.post("http://127.0.0.1:34590",data=tokenized.encode("utf-8"))
        tagged=r_tag.text
        r_parse=requests.post("http://127.0.0.1:34591",data=tagged.encode("utf-8"))
        parsed=r_parse.text
        print(parsed,end="")

        
