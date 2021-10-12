import subprocess
import os.path
import sys
import hashlib
import io
import http.server
import urllib
import argparse

import onmt
import configargparse
from onmt.translate.translator import build_translator
from onmt.utils.parse import ArgumentParser
from onmt.model_builder import build_base_model
import torch
from onmt.translate import Translator


ID,FORM,LEMMA,UPOS,XPOS,FEATS,HEAD,DEPREL,DEPS,MISC=range(10)
WHITESPACE_MARKER = "$@@$"

def read_conllu(f):
    sent=[]
    comment=[]
    for line in f:
        line=line.strip()
        if not line: # new sentence
            if sent:
                yield comment,sent
            comment=[]
            sent=[]
        elif line.startswith("#"):
            comment.append(line)
        else: #normal line
            sent.append(line.split("\t"))
    else:
        if sent:
            yield comment, sent

class Lemmatizer(object):

    def __init__(self):
        # empty init
        # use init_model() to initialize the model before prediction
        self.model_ready=False
        pass
        
        
    def init_model(self, args):
        
        use_gpu = True if torch.cuda.is_available() else False
        device = 0 if use_gpu else -1
        print("Lemmatizer device:", "gpu" if use_gpu else "cpu", "/", device, file=sys.stderr)

        self.batch_size = args.batch_size

        # make virtual files to collect the predicted output (not actually needed but opennmt still requires this)
        self.f_output=io.StringIO()

        self.translator = self.build_my_translator(args.model, self.f_output, use_gpu=use_gpu, gpu_device=device, beam_size=args.beam_size, max_length=args.max_length)

        self.localcache={} #tokendata -> lemma  #remembered by this process, lost thereafter
        self.model_ready=True
        
        
    def load_model(self, model, use_gpu=False, gpu_device=-1, fp32=False):

        checkpoint = torch.load(model, map_location=lambda storage, loc: storage)
        model_opt = ArgumentParser.ckpt_model_opts(checkpoint['opt'])
        ArgumentParser.update_model_opts(model_opt)
        ArgumentParser.validate_model_opts(model_opt)
        fields = checkpoint['vocab']

        model = build_base_model(model_opt, fields, use_gpu, checkpoint, gpu_device) # use_gpu = True/False, gpu_device = int/None
        if fp32:
            model.float()
        model.eval()
        model.generator.eval()
        return fields, model, model_opt



    def build_my_translator(self, model_name, out_file, use_gpu=False, gpu_device=-1, beam_size=5, max_length=50):

        fields, model, model_opt = self.load_model(model_name, use_gpu=use_gpu, gpu_device=gpu_device)

        scorer = onmt.translate.GNMTGlobalScorer(0.0, -0.0, 'none', 'none') # alpha, beta, length_penalty, coverage_penalty

        src_reader = onmt.inputters.str2reader["text"]()
        tgt_reader = onmt.inputters.str2reader["text"]()

        translator = Translator(
                model,
                fields,
                src_reader,
                tgt_reader,
                gpu=gpu_device, # gpu device, negative for no gpu
                n_best=1,
                min_length=0,
                max_length=max_length,
                ratio=-0.0,
                beam_size=beam_size,
                random_sampling_topk=1,
                random_sampling_temp=1.0,
                stepwise_penalty=False,
                dump_beam=False,
                block_ngram_repeat=0,
                ignore_when_blocking=set([]),
                replace_unk=True,
                tgt_prefix=False,
                phrase_table="",
                data_type="text",
                verbose=False,
                report_time=False,
                copy_attn=model_opt.copy_attn,
                global_scorer=scorer,
                out_file=out_file,
                report_align=False,
                report_score=False,
                logger=None,
                seed=-1)
        return translator




    def lemmatize_batch(self, data_batch):
        """ Lemmatize one data batch """
        
        if self.model_ready==False:
            print("\nERROR: Lemmatizer.init_model() must be called before prediction!\n", file=sys.stderr)
            sys.exit(1)

        submitted=set() #set of submitted tokens
        submitted_tdata=[] #list of token data entries submitted for lemmatization

        # lemmatize data_batch
        original_sentences=[]
        translate_input=[]
        token_counter=0
        for (comm, sent) in read_conllu(data_batch.split("\n")):
            original_sentences.append((comm, sent))
            for token in sent:
                if "-" in token[ID]: # multiword token line, not supposed to be analysed
                    continue
                token_counter+=1
                if token[LEMMA]!="_": # already filled in for example by another module, do not process
                    continue
                token_data=(token[FORM],token[UPOS],token[FEATS])
                if token_data not in self.localcache and token_data not in submitted:
                    submitted.add(token_data)
                    submitted_tdata.append(token_data)
                    form, _ = self.transform_token(token)
                    translate_input.append(form)
        print(" >>> {}/{} unique tokens submitted to lemmatizer".format(len(submitted_tdata),token_counter),file=sys.stderr)
        # run lemmatizer if everything is not in cache
        if len(submitted_tdata)>0:

            scores, predictions=self.translator.translate(translate_input, batch_size=self.batch_size)
            self.f_output.truncate(0) # clear this to prevent eating memory

            lemm_output=[l[0] for l in predictions]
            for tdata,predicted_lemma in zip(submitted_tdata,lemm_output):
                predicted_lemma=self.detransform_string(predicted_lemma.strip())
                self.localcache[tdata]=predicted_lemma
        output_lines=[]
        for comm, sent in original_sentences:
            for c in comm:
                output_lines.append(c)
            for cols in sent:
                if "-" in cols[ID] or cols[LEMMA]!="_": # multiword token line or lemma already predicted, not supposed to be analysed
                    output_lines.append("\t".join(t for t in cols))
                    continue
                token_data=(cols[FORM],cols[UPOS],cols[FEATS])
                if token_data in self.localcache:
                    plemma=self.localcache[token_data]
                else:
                    assert False, ("Missing lemma", token_data)
                if plemma.strip()=="":
                    plemma="_" # make sure not to output empty lemma
                cols[LEMMA]=plemma
                output_lines.append("\t".join(t for t in cols))
            output_lines.append("")


        return "\n".join(output_lines)+"\n"


    def transform_token(self, cols):

        input_chars = " ".join(c if c != " " else WHITESPACE_MARKER for c in cols[FORM])
        features = " ".join([cols[UPOS]] + cols[FEATS].split("|")) # add morphological features
        input_chars = input_chars + " " + features
        
        lemma_chars = " ".join(c if c != " " else WHITESPACE_MARKER for c in cols[LEMMA])

        return input_chars, lemma_chars

    def detransform_string(self, token):

        chars=[]
        for t in token.split(" "):
            if t==WHITESPACE_MARKER:
                chars.append(" ")
                continue
            if len(t)>1 and "=" in t: # leaked pos or morphological tag because of -replace_unk
                continue 
            chars.append(t)
        chars = "".join(chars).strip()
        if chars == "":
            chars = "_"
        return chars



class LemmatizerWrapper():

    def __init__(self, args):
        """
        Lemmatizer model loading
        """

        self.lemmatizer_model=Lemmatizer()
        self.lemmatizer_model.init_model(args)
        pass

            
    def parse_text(self,conllu):
        result_conllu=self.lemmatizer_model.lemmatize_batch(conllu)
        return result_conllu

def launch(args,q_in,q_out):

    lemmatizer=LemmatizerWrapper(args)
    while True:
        jobid,txt=q_in.get()
        if jobid=="FINAL":
            q_out.put((jobid,txt))
            print("Lemmatizer exiting",file=sys.stderr,flush=True)
            return
        q_out.put((jobid,lemmatizer.parse_text(txt)))

argparser = argparse.ArgumentParser(description='Lemmatize conllu text')
argparser.add_argument('--model', default='models/lemmatizer.pt', type=str, help='Model')
argparser.add_argument('--device', type=int, default=0, help='Deprecated, uses GPU if available.')
argparser.add_argument('--batch_size', type=int, default=256, help='Batch size')
argparser.add_argument('--max_length', type=int, default=50, help='Maximum predicted sequence length')
argparser.add_argument('--beam_size', type=int, default=5, help='Decoding beam size')

