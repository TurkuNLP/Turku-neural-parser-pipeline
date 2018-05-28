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

class TaggerHTTPDummyHandler(dummy_handler.DummyHandler):

    pass

class ParserHTTPDummyHandler(dummy_handler.DummyHandler):

    pass


def launch(args,handler_class):
    parser=parser_lib.NetworkParserWrapper(args.model,args.parser_dir)
    handler_class.parser=parser
    httpd = http.server.HTTPServer(("",args.port), handler_class)
    httpd.serve_forever()

argparser = argparse.ArgumentParser(description='Parse/Tag conllu text')
argparser.add_argument('--port', metavar='TCP port', type=int, default=32787, help='port')
argparser.add_argument('--model', default="/usr/share/ParseBank/TinyFinnish-Stanford-model/Finnish-Tagger", help='Model. Default: %(default)s')
argparser.add_argument('--parser-dir', default="Parser-v2", help='Parser. Default: ./%(default)s')

if __name__=="__main__":
    args=argparser.parse_args()
    launch(args)
