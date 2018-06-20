# Finnish neural dependency parser

A new take on the trusty old Finnish-dep-parser. The current pipeline is fully neural and has a substantially better accuracy in all layers of annotation.

# Installation

## Download the code

Clone the parser as well as all of its submodules as follows:

    git clone https://github.com/TurkuNLP/Finnish-dep-parser-neural.git
    cd Finnish-dep-parser-neural
    git submodule update --init --recursive

## Setup Python environment

We highly recommend that you make a virtual environment for the parser:

    python3 -m venv venv-parser-neural
    source venv-parser-neural/bin/activate

Then you need to install the necessary libraries:

    pip3 install -r requirements-gpu.txt

or
   
    pip3 install -r requirements-cpu.txt

## Install pytorch

You also need to install PyTorch by selecting the appropriate options from https://pytorch.org/. For a typical
GPU install you would select something like "Linux - pip - 3.5 - CUDA 9.1" matching the version of your python and CUDA.
If you run on CPU and have no CUDA, then select None.

1. Run the commands which pytorch.org gives
2. Run yet `pip3 install torchtext` when (1) is ready and you're done

## Download the models

All models are available [here](http://bionlp-www.utu.fi/dep-parser-models) and you can use the following utility script to fetch the model:

    python3 fetch_models.py fi_tdt

# Running the parser

The parser has these properties:

* a relatively long start-up cost when it's loading the models (see the server mode to prevent model reloading)
* memory-hungry (this is on our todo, bear with us)
* very fast when parsing large documents because of the mini-batch style of computing
* efficient use of GPU, about 5x faster than the previous Finnish-dep-parser (which could not use GPU for anything)
* transparent passing through metadata

## Metadata in input

In the input data, all lines which start with `###C:` are treated as metadata and will be passed through the pipeline unmodified, and attached in the conllu output to the following sentence. This is an easy way to pass metadata through the pipeline. Note that since the conllu format attaches metadata to sentences, the last line of a file cannot be the `###C:` comment. It is fine to have several comment lines one after another.

## Pipelines

Various pipelines can be built out of the various components of the parser and these are generally defined in model_directory/pipelines.yaml. You can also list what you have like so:

    python3 full_pipeline_stream.py --conf models_fi_tdt/pipelines.yaml list

For Finnish these are:

* `parse_plaintext` read plain text, tokenize, split into sentences, tag, parse, lemmatize
* `parse_sentlines` read text one sentence per line, tokenize, tag, parse, lemmatize
* `parse_wsline` read whitespace tokenized text one sentence per line, tag, parse, lemmatize
* `parse_conllu` read conllu, tag, parse, lemmatize

Other pipelines (which skip some of these steps etc) can be built easily by mimicking the existing pipelines in the `pipelines.yaml` (also see below)

## Stream mode

In the stream mode, the parser reads from stdin, outputs to stdout

    cat myfile.txt | python3 full_pipeline_stream.py --conf models_fi_tdt/pipelines.yaml parse_plaintext > myfile.conllu

## Server mode

In the server mode, the parser loads all models and parses in a batch style. Docs TODO.

# pipelines.yaml file

For those who wish to hack the pipelines.yaml file. You can add `extraoptions` to enforce some parameters applied as if you gave them on the command line. This is curently only used to enforce batching on empty lines in pipelines that parse conllu, making sure the input is not cut in the middle of the line. As you can probably figure out, the pipeline simply specifies which modules are launched and their parameters, new steps to the pipeline are easy to add by mimicking the `*_mod.py` files.