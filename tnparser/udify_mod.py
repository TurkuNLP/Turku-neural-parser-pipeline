import os.path
import sys
import io
import argparse
import traceback
import tarfile
from pathlib import Path
from tempfile import NamedTemporaryFile

import tnparser.udify as udify
import tnparser.udify.util

from allennlp.predictors.predictor import Predictor
from allennlp.models.archival import load_archive
from allennlp.common.checks import check_for_gpu
from allennlp.common import Params
from allennlp.common.util import import_submodules
from allennlp.commands.predict import _PredictManager
from allennlp.common.util import lazy_groups_of


def read_conllu(txt):
    sent=[]
    comment=[]
    for line in txt.split("\n"):
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
            


class UdifyWrapper():

    def __init__(self, args):
        """
        Udify model loading etc goes here
        """
        
        # config
        import_submodules("tnparser.udify") # this registers udify_model into allennlp lib
        archive_dir = Path(args.model).resolve().parent # where to extract the model

        if not os.path.isfile(archive_dir / "weights.th"):
            with tarfile.open(args.model) as tar:
                tar.extractall(archive_dir)

        config_file = archive_dir / "config.json"

        overrides = {}
        if args.device is not None:
            overrides["trainer"] = {"cuda_device": args.device}
        if args.lazy:
            overrides["dataset_reader"] = {"lazy": args.lazy}
       
        configs = [Params(overrides), Params.from_file(config_file)]

        params = tnparser.udify.util.merge_configs(configs)
        
        predictor = "udify_predictor" if not args.raw_text else "udify_text_predictor"
        
        # params
        self.cuda_device = params["trainer"]["cuda_device"]
        self.batch_size = args.batch_size
        
        check_for_gpu(self.cuda_device)
        
        # load model
        archive = load_archive(args.model, cuda_device=self.cuda_device)

        self.predictor = Predictor.from_archive(archive, predictor)
        
        print("Dataset reader:", self.predictor._dataset_reader.__class__, file=sys.stderr)
        
    def data_iter(self, fname):
        yield from self.predictor._dataset_reader.read(fname)
            
            
    def _predict_instances(self, batch_data):
        if len(batch_data) == 1:
            results = [self.predictor.predict_instance(batch_data[0])]
        else:
            results = self.predictor.predict_batch_instance(batch_data)
        for output in results:
            yield self.predictor.dump_line(output)
            
    def conllu_comments(self, txt):
        # returns comments (list) of each sentence
        comments = []
        for comm, sent in read_conllu(txt):
            comments.append(comm)
        return comments
        
    def parse_text(self, txt):
    
        comments = self.conllu_comments(txt)
        
        f_input = NamedTemporaryFile()
    
        with open(f_input.name, "wt", encoding="utf-8") as f:
            print(txt, end="", file=f)
            
        
        # insides of run()
        parsed_txt = ""
        for batch in lazy_groups_of(self.data_iter(f_input.name), self.batch_size):
            for model_input_instance, result in zip(batch, self._predict_instances(batch)):
                parsed_txt += result
            
        f_input.close()
        
        # merge comments and text
        sentences = [sent for comm, sent in read_conllu(parsed_txt)]
        assert len(comments) == len(sentences)
        parsed_txt = ""
        for comm, sent in zip(comments, sentences):
            for c in comm:
                parsed_txt += c+"\n"
            for token in sent:
                parsed_txt += "\t".join(token) + "\n"
            parsed_txt += "\n"

        return parsed_txt
        




def launch(args, q_in, q_out):
    try:
        parser = UdifyWrapper(args)
    except:
        traceback.print_exc()
        sys.stderr.flush()
    while True:
        jobid,txt=q_in.get()
        if jobid=="FINAL":
            q_out.put((jobid,txt))
            return
        try:
            conllu=parser.parse_text(txt)
            q_out.put((jobid,conllu))
        except:
            traceback.print_exc()
            sys.stderr.flush()
            
        
        
argparser = argparse.ArgumentParser()
argparser.add_argument("--model", type=str, help="The archive file")
argparser.add_argument("--device", default=0, type=int, help="CUDA device number; set to -1 for CPU")
argparser.add_argument("--batch_size", default=128, type=int, help="The size of each prediction batch")
argparser.add_argument("--lazy", action="store_true", help="Lazy load dataset")
argparser.add_argument("--raw_text", action="store_true", help="Input raw sentences, one per line in the input file.")
        
        

