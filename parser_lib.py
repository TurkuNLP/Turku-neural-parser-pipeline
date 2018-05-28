#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2016 Timothy Dozat
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os

#Add the parser path
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),"Parser-v2"))

import re
import os
import sys
import codecs
from argparse import ArgumentParser

from parser import Configurable
from parser import Network
import io
import os

class NetworkParserWrapper:

  def __init__(self,save_dir,parser_dir):
    argparser = ArgumentParser('Network')
    argparser.add_argument('--save_dir', required=True)
    subparsers = argparser.add_subparsers()
    section_names = set()
    # --section_name opt1=value1 opt2=value2 opt3=value3
    with codecs.open(os.path.join(parser_dir,'config/defaults.cfg')) as f:
      section_regex = re.compile('\[(.*)\]')
      for line in f:
        match = section_regex.match(line)
        if match:
          section_names.add(match.group(1).lower().replace(' ', '_'))

    #===============================================================
    # Parse
    #---------------------------------------------------------------
    def parse(save_dir, **kwargs):
      """ """
      kwargs['config_file'] = os.path.join(save_dir, 'config.cfg')
      files = kwargs.pop('files')
      if not files:
        files=[sys.stdin]
      output_file = kwargs.pop('output_file', None)
      output_dir = kwargs.pop('output_dir', None)
      if len(files) > 1 and output_file is not None:
        raise ValueError('Cannot provide a value for --output_file when parsing multiple files')
      kwargs['is_evaluation'] = True
      network = Network(**kwargs)
      print("Done building net",file=sys.stderr)
      #network.batch_parse(files, output_file=output_file, output_dir=output_dir)
      return network
    #---------------------------------------------------------------

    parse_parser = subparsers.add_parser('parse')
    parse_parser.set_defaults(action=parse)
    parse_parser.add_argument('files', nargs='*')
    for section_name in section_names:
      parse_parser.add_argument('--'+section_name, nargs='+')
    parse_parser.add_argument('--output_file')
    parse_parser.add_argument('--output_dir')


    #***************************************************************
    # Parse the arguments
    kwargs = vars(argparser.parse_args(["--save_dir",save_dir,"parse"]))
    action = kwargs.pop('action')
    save_dir = kwargs.pop('save_dir')
    kwargs = {key: value for key, value in kwargs.items() if value is not None}
    for section, values in kwargs.items():
      if section in section_names:
        values = [value.split('=', 1) for value in values]
        kwargs[section] = {opt: value for opt, value in values}
    if 'default' not in kwargs:
      kwargs['default'] = {}
    kwargs['default']['save_dir'] = save_dir
    self.network=action(save_dir, **kwargs)  


    self.parse_generator=self.network.parse_generator()
    self.network.current_input=io.StringIO(self.network.dummy_sents_hack()) #parse some dummy data to get everything initialized
    self.parse_generator.__next__()
    
  def parse_text(self,conllu):
    self.network.current_input=io.StringIO(self.network.dummy_sents_hack()+conllu)
    return self.parse_generator.__next__()

#  --------------------
  
def txt_to_conllu(sentences):
  """Just a quick dummy to turn list of whitespace-tokenized sentences into conllu"""
  buff=io.StringIO()
  for s in sentences:
    for idx,wrd in enumerate(s.split()):
      print(idx+1,wrd,"_","_","_","_","_","_","_","_",sep="\t",file=buff)
    print(file=buff)
  print("ENTERS PARSER",repr(buff.getvalue()),file=sys.stderr)
  return buff.getvalue()

if __name__=="__main__":
  net_wrapper=NetworkParserWrapper("/usr/share/ParseBank/TinyFinnish-Stanford-model/Finnish-Tagger","Parser-v2")
  print(net_wrapper.parse_text(txt_to_conllu(["Minulla on koira !","Syön makkaraa ja vihaan opiskelijoita ."])),end="")
  print(net_wrapper.parse_text(txt_to_conllu(["Seuraava yritys ..."])),end="")
  
  
  
                                  
