import os.path
import sys
import hashlib
import io
import parser_lib
import http.server
import urllib
import dummy_handler
import argparse

class TokenizerHTTPDummyHandler(dummy_handler.DummyHandler):

    pass


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

def launch(args):
    t=TokenizerWrapper()
    TokenizerHTTPDummyHandler.parser=t #set this as a class attribute
    httpd = http.server.HTTPServer(("",args.port), TokenizerHTTPDummyHandler)
    httpd.serve_forever()
    
argparser = argparse.ArgumentParser(description='Tokenize text')
argparser.add_argument('--port', metavar='TCP port', type=int, default=32786, help='port')


if __name__ == '__main__':
    args=parser.parse_args()
    launch(args)
    

    # pw.parse_text("Minulla on koira")
    # pw.parse_text("Minulla on kissakin")
    # pw.parse_text("Minulla on kissakin\nJa toinen lause")
    # app.run(debug=False, port=5957, use_reloader=False)
