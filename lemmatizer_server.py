
import subprocess
import os.path
import sys
import hashlib
import io
import parser_lib
import http.server
import urllib
import dummy_handler

class LemmatizerHTTPDummyHandler(dummy_handler.DummyHandler):

    pass


class LemmatizerWrapper():

    def __init__(self):
        """
        Tokenizer model loading etc goes here
        """
        pass
            
    def parse_text(self,conllu):
        return conllu

def launch(args):
    handler_class=LemmatizerHTTPDummyHandler
    lemmatizer=None #HERE IT GOES
    handler_class.parser=lemmatizer
    httpd = http.server.HTTPServer(("",args.port), handler_class)
    httpd.serve_forever()

argparser = argparse.ArgumentParser(description='Lemmatize conllu text')
argparser.add_argument('--port', metavar='TCP port', type=int, default=32787, help='port')

if __name__=="__main__":
    args=argparser.parse_args()
    launch(args)
