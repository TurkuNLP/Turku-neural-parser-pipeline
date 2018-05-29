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

def launch(args,q_in,q_out):
    parser=parser_lib.NetworkParserWrapper(args.model,args.parser_dir)
    while True:
        txt=q_in.recv()
        q_out.send(parser.parse_text(txt))
        
argparser = argparse.ArgumentParser(description='Parse/Tag conllu text')
argparser.add_argument('--model', default="/usr/share/ParseBank/TinyFinnish-Stanford-model/Finnish-Tagger", help='Model. Default: %(default)s')
argparser.add_argument('--parser-dir', default="Parser-v2", help='Parser. Default: ./%(default)s')

