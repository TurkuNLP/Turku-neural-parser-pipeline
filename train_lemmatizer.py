"""
A bit experimental script for training new models for lemmatization

"""

import os
import sys
import glob
from shutil import copyfile, rmtree
import re
from distutils.util import strtobool
import yaml
import torch

from tnparser.lemmatizer_mod import Lemmatizer, read_conllu

ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC = range(10)

thisdir=os.path.dirname(os.path.realpath(__file__))


def numeric_sort(x):
    r = re.compile('(\d+)')
    l = r.split(x)
    return [int(y) if y.isdigit() else y for y in l]


def copy_lemmatizer(args):

    files=glob.glob(f"{args.name}/lemmatizer_step_*.pt".format(name=args.name))
    latest=sorted(files, key =numeric_sort)[-1]
    print(f"Copying the latest checkpoint {latest} into {args.name}/lemmatizer.pt", file=sys.stderr)
    copyfile(latest, f"{args.name}/lemmatizer.pt")


def create_dataset(fname):
    lemmatizer = Lemmatizer()
    data=[]
    with open(fname, "rt", encoding="utf-8") as f:
        for comm, sent in read_conllu(f):
            for token in sent:
                word, lemma = lemmatizer.transform_token(token)
                data.append((word, lemma))    
    return data
    
    
def print_train_data(train, devel, path):

    with open(os.path.join(path, "train.input"), "wt", encoding="utf-8") as inpf, open(os.path.join(path, "train.output"), "wt", encoding="utf-8") as outf:
        for (word, lemma) in train:
            print(word, file=inpf)
            print(lemma, file=outf)
            
    with open(os.path.join(path, "devel.input"), "wt", encoding="utf-8") as inpf, open(os.path.join(path, "devel.output"), "wt", encoding="utf-8") as outf:
        for (word, lemma) in devel:
            print(word, file=inpf)
            print(lemma, file=outf)


def build_config(args):

    # basic params
    params = {}
    discard = ["name", "train_file", "devel_file", "force_overwrite"] # these needs different handling
    for key, value in vars(args).items():
        if key not in discard:
            params[key] = value
            
    # data params
    params["save_data"] = f"{args.name}/lemmatizer-data" # place to save processed data
    params["src_vocab"] = f"{args.name}/lemmatizer-data.vocab.src" # save vocab
    params["tgt_vocab"] = f"{args.name}/lemmatizer-data.vocab.tgt" # save vocab
    params["overwrite"] = True # overwrite old data if exists
    
    data = {}
    data["corpus_1"] = {} # train corpus
    data["corpus_1"]["path_src"] = f"{args.name}/train.input"
    data["corpus_1"]["path_tgt"] = f"{args.name}/train.output"
    data["valid"] = {} # valid corpus
    data["valid"]["path_src"] = f"{args.name}/devel.input"
    data["valid"]["path_tgt"] = f"{args.name}/devel.output"
    params["data"] = data
    
    # GPU if available
    if torch.cuda.is_available():
        params["world_size"] = 1
        params["gpu_ranks"] = [0]
    else:
        print("Warning! GPU not available, training the lemmatizer may take very long!", file=sys.stderr)
    
    # defaults
    params["encoder_type"] = "brnn"
    params["early_stopping"] = 4
    params["early_stopping_criteria"] = "accuracy"
            
    with open(f"{args.name}/config.yaml", "wt", encoding="utf-8") as f:
        yaml.dump(params, f)
        
    print(f"Lemmatizer config created, saved at {args.name}/config.yaml", file=sys.stderr)
    
            
def train_model(args):

    # data
    preprocess = f"onmt_build_vocab -config {args.name}/config.yaml -n_sample 500000"
    print(f"Running command: {preprocess}", file=sys.stderr)
    status = os.system(preprocess)
    if status != 0:
        print("Lemmatizer status:", status, "Preprocessing failed.", file=sys.stderr)
        sys.exit()
        
    # train model
    use_gpu = True if torch.cuda.is_available() else False
    if use_gpu == False:
        print("Warning! Training the lemmatizer on CPU, this may take very long!", file=sys.stderr)
        
    train = f"onmt_train -config {args.name}/config.yaml -save_model {args.name}/lemmatizer"
    print(f"Running command: {train}", file=sys.stderr)
    status = os.system(train)
    if status != 0:
        print("Lemmatizer status:", status, "Training failed.", file=sys.stderr)
        sys.exit()
     
    # TODO: continue here
    copy_lemmatizer(args) # copy the latest lemmatizer under correct name

    print("Building lemma cache...", file=sys.stderr)
    status = os.system(f"cat {args.train_file} | python3 {thisdir}/build_lemma_cache.py > {args.name}/lemma_cache.tsv") # build lemma cache
    if status != 0:
        print("Lemma cache status:", status, "Training failed.", file=sys.stderr)
        sys.exit()



def train(args):

    build_config(args)
    
    train_data = create_dataset(args.train_file)
    devel_data = create_dataset(args.devel_file)
    print_train_data(train_data, devel_data, args.name)
    print("Data created.", file=sys.stderr)
    train_model(args)



if __name__=="__main__":
    import argparse
    argparser = argparse.ArgumentParser(description='Lemmatizer training')
    required_group = argparser.add_argument_group("Training parameters")
    required_group.add_argument('--name', default="lemmatizer-model", help='Model directory name')
    required_group.add_argument('--train_file', type=str, required=True, help='Training data file (conllu)')
    required_group.add_argument('--devel_file', type=str, required=True, help='Development data file (conllu)')
    required_group.add_argument('--force_overwrite', action="store_true", default=False, help='Overwrite old files without asking (default: False, ask before overwriting)')

    optional_group = argparser.add_argument_group("Model parameters")
    optional_group.add_argument('--min_char_freq', type=int, default=5, help='Minimum character frequency to keep, rest will be replaced with unknown (default: 5)')
    optional_group.add_argument('--dropout', type=float, default=0.3, help='Dropout (default: 0.3)')
    optional_group.add_argument('--optim', type=str, default="adam", help='Optimizer (adam/sgd, default: adam)')
    optional_group.add_argument('--learning_rate', type=float, default=0.0005, help='Learning rate (default: 0.0005)')
    optional_group.add_argument('--learning_rate_decay', type=float, default=0.9, help='Learning rate decay (default: 0.9)') #TODO
    optional_group.add_argument('--warmup_steps', type=float, default=1000, help='Warmup steps (default: 1000)')
    optional_group.add_argument('--batch_size', type=int, default=64, help='Batch size (default: 64)')
    optional_group.add_argument('--train_steps', type=int, default=50000, help='Train N steps (default: 50,000)')
    optional_group.add_argument('--valid_steps', type=int, default=2000, help='Validate every N steps (default: 2000)')
    optional_group.add_argument('--save_every_steps', type=int, default=2000, help='Save every N steps (default: 2000)')
    optional_group.add_argument('--report_every', type=int, default=2000, help='Report every N steps (default: 2000)')
    optional_group.add_argument('--save_checkpoint_steps', type=int, default=2000, help='Save every N steps (default: 2000)')
    optional_group.add_argument('--keep_checkpoint', type=int, default=25, help='Keep N latest cheeckpoints (default: 25)')
    
    args = argparser.parse_args()



    # manage directories
    try:
        if os.path.isdir(args.name):
            files=[]
            for dirpath, dirnames, filenames in os.walk(args.name):
                for fname in filenames:
                    files.append(os.path.join(dirpath, fname))
            if args.force_overwrite == False:
                input(f'\nDirectory {args.name}/ already exists, old files will be deleted. Press <Enter> to continue or <Ctrl-c> to abort.\n')
                input('\nDeleting files [{files}] from directory {directory}/. Press <Enter> to continue or <Ctrl-c> to abort.\n'.format(files=", ".join(files),directory=args.name))
            for f in files:
                print("Deleting",f,file=sys.stderr)
                os.remove(f)
        else:
            os.mkdir(args.name)
    except KeyboardInterrupt:
        print(file=sys.stderr)
        sys.exit(0)

    # train
    train(args)
