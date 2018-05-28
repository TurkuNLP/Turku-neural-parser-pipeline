
import subprocess
import os.path
import sys
import hashlib
import io
import parser_lib
import http.server
import urllib
import dummy_handler

class LemmatizerWrapper():

    def __init__(self):
        """
        Tokenizer model loading etc goes here
        """
        pass
            
    def parse_text(self,conllu):
        return conllu


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Tokenize text')
    parser.add_argument('--port', metavar='TCP port', type=int, default=32789, help='port')
    args=parser.parse_args()
    lemmatizer=LemmatizerWrapper()
    dummy_handler.DummyHandler.parser=lemmatizer #set this as a class attribute
    httpd = http.server.HTTPServer(("",args.port), dummy_handler.DummyHandler)
    httpd.serve_forever()

    # pw.parse_text("Minulla on koira")
    # pw.parse_text("Minulla on kissakin")
    # pw.parse_text("Minulla on kissakin\nJa toinen lause")
    # app.run(debug=False, port=5957, use_reloader=False)
