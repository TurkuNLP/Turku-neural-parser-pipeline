"""
A bit experimental script for training new models for tagging, parsing and lemmatization
TODO: Currently tokenizer must be trained manually from command line (for instructions see docs/training.md)

Parameters are obtained from templates/lemmatizer.yaml, templates/parser.cfg, templates/tagger.cfg, templates/tokenizer.cfg
--> By defaut it will use same parameters as in the TurkuNLP CoNLL-18 models, but you can change the hyperparameter settings in these files if you wish
"""

import os
import sys
import glob
from shutil import copyfile, rmtree
import re
from distutils.util import strtobool

thisdir=os.path.dirname(os.path.realpath(__file__))

def create_model_directory(args):


    # create necessary directories
    if os.path.isdir("models_{name}".format(name=args.name)):
        print("Directory models_{name} already exists, old files will be overwritten".format(name=args.name), file=sys.stderr)
        
    else:
        os.mkdir("models_{name}".format(name=args.name))
        os.mkdir("models_{name}/Data".format(name=args.name))
        os.mkdir("models_{name}/Tokenizer".format(name=args.name))

    # copy necessary files
    if args.embeddings: # embeddings
        copyfile(args.embeddings, "models_{name}/Data/embeddings.vectors".format(name=args.name))
    copyfile("{workdir}/{config}/pipelines.yaml".format(workdir=thisdir, config=args.config_directory), "models_{workdir}/pipelines.yaml".format(workdir=args.name))
    process_morpho(args) # train/dev files for tagger/parser
    process_config(args) # configs for tagger/parser
    
    

def process_config(args):

    with open("{workdir}/{config}/tagger.cfg".format(workdir=thisdir, config=args.config_directory), "rt", encoding="utf-8") as f:
        data=f.read()
        data = data.replace("treebank = placeholder", "treebank = {name}".format(name=args.name))
        with open("models_{name}/tagger.cfg".format(name=args.name), "wt", encoding="utf-8") as z:
            print(data, file=z)

    with open("{workdir}/{config}/parser.cfg".format(workdir=thisdir, config=args.config_directory), "rt", encoding="utf-8") as f:
        data=f.read()
        data = data.replace("treebank = placeholder", "treebank = {name}".format(name=args.name))
        with open("models_{name}/parser.cfg".format(name=args.name), "wt", encoding="utf-8") as z:
            print(data, file=z)

    with open("{workdir}/{config}/lemmatizer.yaml".format(workdir=thisdir, config=args.config_directory), "rt", encoding="utf-8") as f:
        data=f.read()
        data = data.replace("train: placeholder", "train: {train}".format(train=args.train_file))
        data = data.replace("dev: placeholder", "dev: {dev}".format(dev=args.devel_file))
        data = data.replace("model_dir: placeholder", "model_dir: models_{name}/Lemmatizer".format(name=args.name))
        with open("models_{name}/lemmatizer.yaml".format(name=args.name), "wt", encoding="utf-8") as z:
            print(data, file=z)

    return

def process_morpho(args):

    import importlib.util
    spec = importlib.util.spec_from_file_location("main", "{workdir}/../Parser-v2/nparser/scripts/transfer_morpho.py".format(workdir=thisdir))
    morphotransfer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(morphotransfer)

    with open(args.train_file, "rt", encoding="utf-8") as in_, open("models_{name}/Data/train.conllu".format(name=args.name), "wt", encoding="utf-8") as out_:
        morphotransfer.main(False, input_=in_, output_=out_)
    with open(args.devel_file, "rt", encoding="utf-8") as in_, open("models_{name}/Data/dev.conllu".format(name=args.name), "wt", encoding="utf-8") as out_:
        morphotransfer.main(False, input_=in_, output_=out_)
    return

def numeric_sort(x):
    r = re.compile('(\d+)')
    l = r.split(x)
    return [int(y) if y.isdigit() else y for y in l]


def copy_lemmatizer(args):

    files=glob.glob("models_{name}/Lemmatizer/model_step_*.pt".format(name=args.name))
    latest=sorted(files, key =numeric_sort)[-1]
    copyfile(latest, "models_{name}/Lemmatizer/lemmatizer.pt".format(name=args.name))




def train_all(args):

    # tokenizer --- TODO

    # Tagger
    if args.tagger:
        print("Training a tagger", file=sys.stderr)
        status = os.system("python3 {workdir}/../Parser-v2/main.py --save_dir models_{name}/Tagger train --config_file models_{name}/tagger.cfg".format(workdir=thisdir, name=args.name))
        if status != 0:
            print("Tagger status:", status, "Training failed.", file=sys.stderr)
            sys.exit()

    # Parser
    if args.parser:
        print("Training a parser")
        status = os.system("python3 {workdir}/../Parser-v2/main.py --save_dir models_{name}/Parser train --config_file models_{name}/parser.cfg".format(workdir=thisdir, name=args.name))
        if status != 0:
            print("Parser status:", status, "Training failed.", file=sys.stderr)
            sys.exit()

    # Lemmatizer
    if args.lemmatizer == True:
        print("Training a lemmatizer")
        status = os.system("python3 {workdir}/../universal-lemmatizer/train_lemmatizer.py --treebank default --config models_{name}/lemmatizer.yaml".format(workdir=thisdir, name=args.name))
        if status != 0:
            print("Lemmatizer status:", status, "Training failed.", file=sys.stderr)
            sys.exit()

        copy_lemmatizer(args) # copy the latest lemmatizer under correct name

        status = os.system("cat {train} | python3 {workdir}/../build_lemma_cache.py > models_{name}/Lemmatizer/lemma_cache.tsv".format(train=args.train_file, workdir=thisdir, name=args.name)) # build lemma cache
        if status != 0:
            print("Lemma cache status:", status, "Training failed.", file=sys.stderr)
            sys.exit()

    print("Training done", file=sys.stderr)
    












if __name__=="__main__":
    import argparse
    argparser = argparse.ArgumentParser(description='A script for training new models')
    argparser.add_argument('--name', default="mymodel", help='Model name, all trained models will be saved under models_%name" -directory.')
    argparser.add_argument('--config_directory', default="templates", help='Directory where to load config files.')
    argparser.add_argument('--train_file', type=str, required=True, help='Training data file (conllu)')
    argparser.add_argument('--devel_file', type=str, required=True, help='Development data file (conllu)')
    argparser.add_argument('--embeddings', type=str, help='Word Embeddings (in word2vec text format)')

    argparser.add_argument('--tagger', type=lambda x:bool(strtobool(x)), default=True, choices=[True, False], help='Train a tagger (Default:True)')
    argparser.add_argument('--parser', type=lambda x:bool(strtobool(x)), default=True, choices=[True, False], help='Train a parser (Default:True)')
    argparser.add_argument('--lemmatizer', type=lambda x:bool(strtobool(x)), default=True, choices=[True, False], help='Train a lemmatizer (Default:True)')

    args = argparser.parse_args()

    print(args)

    try:
        if os.path.isdir("models_{name}".format(name=args.name)):
            input('Save directory models_{name} already exists. Press <Enter> to continue or <Ctrl-c> to abort.'.format(name=args.name))
            files=[]
            for dirpath, dirnames, filenames in os.walk('models_{name}'.format(name=args.name)):
                for fname in filenames:
                    files.append(os.path.join(dirpath, fname))
            input('Deleting {files}. Press <Enter> to continue or <Ctrl-c> to abort.'.format(files=", ".join(files)))
            for f in files:
                print("Deleting",f,file=sys.stderr)
                os.remove(f)
    except KeyboardInterrupt:
        print(file=sys.stderr)
        sys.exit(0)

    create_model_directory(args)

    train_all(args)
