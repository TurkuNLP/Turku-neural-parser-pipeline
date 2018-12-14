# Turku neural parser pipeline
A neural parsing pipeline for **segmentation, morphological tagging, dependency parsing and lemmatization with pre-trained models for more than 50 languages**. The pipeline ranked **1st on lemmatization, and 2nd on both LAS and MLAS** (morphology-aware LAS) on the CoNLL-18 Shared Task on Parsing Universal Dependencies. Accuracies for all languages, see TurkuNLP at http://universaldependencies.org/conll18/results.html.

```
LATEST:

Dec 14, 2018: Faster lemmatizer, major updates for the lemmatizer making it considerably faster (no changes in accuracy).
    --> Pipeline needs clean instalation (requirements also changed)!

Dec 13, 2018: Memory leak fixed, should not accumulate RAM with large data streams anymore.

```

## Finnish neural dependency parser

A new take on the trusty old Finnish-dep-parser. The current pipeline is fully neural and has a substantially better accuracy in all layers of annotation. These are the current numbers, measured using the CoNLL18 ST evaluation script on Finnish-TDT UD ver 2.2 data. **This is the "fi_tdt" model distributed with the parser**

```
Metric     | Precision |    Recall |  F1 Score | AligndAcc
-----------+-----------+-----------+-----------+-----------
Tokens     |     99.74 |     99.63 |     99.69 |
Sentences  |     88.55 |     85.02 |     86.75 |
Words      |     99.74 |     99.63 |     99.69 |
UPOS       |     96.63 |     96.52 |     96.57 |     96.88
XPOS       |     97.66 |     97.55 |     97.61 |     97.92
UFeats     |     95.47 |     95.36 |     95.41 |     95.71
AllTags    |     94.03 |     93.92 |     93.97 |     94.27
Lemmas     |     95.30 |     95.19 |     95.24 |     95.54
UAS        |     89.04 |     88.94 |     88.99 |     89.27
LAS        |     86.53 |     86.43 |     86.48 |     86.75
CLAS       |     85.24 |     85.21 |     85.22 |     85.46
MLAS       |     79.86 |     79.83 |     79.85 |     80.07
BLEX       |     81.07 |     81.04 |     81.05 |     81.27
``` 

# Installation

## Prerequisites

For Ubuntu-based systems, the pre-requisities are

    sudo apt install build-essential python3-dev python3-virtualenv python3-tk

## Download the code

Clone the parser as well as all of its submodules as follows:

    git clone https://github.com/TurkuNLP/Turku-neural-parser-pipeline.git
    cd Turku-neural-parser-pipeline
    git submodule update --init --recursive

## Setup Python environment

We highly recommend that you make a virtual environment for the parser and install the `wheel` package:

    python3 -m venv venv-parser-neural
    source venv-parser-neural/bin/activate
    pip3 install wheel

Then you need to install the necessary libraries:

    pip3 install -r requirements-gpu.txt

or
   
    pip3 install -r requirements-cpu.txt

## Install pytorch

In case pytorch would not install correctly through pip, you may need to install PyTorch by selecting the appropriate options from https://pytorch.org/. For a typical
GPU install you would select something like "Linux - pip - 3.5 - CUDA 9.1" matching the version of your python and CUDA.
If you run on CPU and have no CUDA, then select None.

1. Run the `commands which pytorch.org gives`
2. Run yet `pip3 install torchtext` when (1) is ready and you're done

## Download the models

All models are available [here](http://bionlp-www.utu.fi/dep-parser-models) and you can use the following utility script to fetch the model you need:

    python3 fetch_models.py fi_tdt

# Running the parser -- short version

In the basic streaming mode `full_pipeline_stream.py`, the parser reads from stdin, outputs to stdout. You need to give it a file with pipelines (distributed together with each model), and you need to tell it which pipeline to run (parse_plaintext for running segmentation, tagging, syntax and lemmatization; parse_conllu for running tagger, syntax and lemmatization for presegmented conllu-file). So after downloading a model, you can run the parser as (with GPU lemmatizer):

    cat myfile.txt | python3 full_pipeline_stream.py --conf models_fi_tdt/pipelines.yaml --pipeline parse_plaintext > myfile.conllu
    
or (with CPU lemmatizer)

    cat myfile.txt | python3 full_pipeline_stream.py --gpu -1 --conf models_fi_tdt/pipelines.yaml --pipeline parse_plaintext > myfile.conllu


# Running the parser -- long version

The parser has these properties:

* a long start-up cost when it's loading the models (see the server mode to prevent model reloading)
* very fast when parsing large documents because of the mini-batch style of computing
* efficient use of GPU, about 5x faster than the previous Finnish-dep-parser (which could not use GPU for anything)
* transparent passing through metadata

## Metadata in input

In the input data, all lines which start with `###C:` are treated as metadata and will be passed through the pipeline unmodified, and attached in the conllu output to the following sentence. This is an easy way to pass metadata through the pipeline, also through tokenizer and sentence splitting. Note that since the conllu format attaches metadata to sentences, the last line of a file cannot be the `###C:` comment. It is fine to have several comment lines one after another.

## Pipelines

Various pipelines can be built out of the components of the parser and these are generally defined in model_directory/pipelines.yaml. You can also list what you have like so:

    python3 full_pipeline_stream.py --conf models_fi_tdt/pipelines.yaml list

For Finnish these are:

* `parse_plaintext` read plain text, tokenize, split into sentences, tag, parse, lemmatize
* `parse_sentlines` read text one sentence per line, tokenize, tag, parse, lemmatize
* `parse_wslines` read whitespace tokenized text one sentence per line, tag, parse, lemmatize
* `parse_conllu` read conllu, wipe existing values from all columns, tag, parse, lemmatize
* `parse_conllu_nolemmas` read conllu, wipe existing values from all columns, tag, parse
* `tokenize` read plain text, tokenize, split into sentences

Other pipelines (which skip some of these steps etc) can be built easily by mimicking the existing pipelines in the `pipelines.yaml` (also see below). If you wish to run conllu input without wipe_mod (which wipes existing values from all columns), note that lemmatizer modules are designed to pass existing lemma values through unchanged and lemmatize only words with empty lemma field (`_`).

## Stream mode

In the stream mode `full_pipeline_stream.py`, the parser reads from stdin, outputs to stdout. You need to give it the file with pipelines and you need to tell it which pipeline to run (parse_plaintext is the default). So you can run the parser as:

    cat myfile.txt | python3 full_pipeline_stream.py --conf models_fi_tdt/pipelines.yaml --pipeline parse_plaintext > myfile.conllu

## Server mode

Docs TODO

# pipelines.yaml file

For those who wish to hack the pipelines.yaml file. You can add `extraoptions` to enforce some parameters applied as if you gave them on the command line. This is curently only used to enforce batching on empty lines in pipelines that parse conllu, making sure the input is not cut in the middle of the line. As you can probably figure out, the pipeline simply specifies which modules are launched and their parameters, new steps to the pipeline are easy to add by mimicking the `*_mod.py` files.

# Speed

**GPU:** The throughput of the full pipeline is on the order of 100 trees/sec on NVIDIA GeForce GTX 1070. In the beginning the reported time looks worse as it includes also model loading, 100 trees/sek is measured after processing 50K sentences.

**CPU:** On my laptop (8 cores + 8GB of RAM) I was able to run approx. 22 trees/sec (measured after processing 20K sentences).

# Referencies

Main reference for the pipeline:
```
@inproceedings{udst:turkunlp,
author = {Jenna Kanerva and Filip Ginter and Niko Miekka and Akseli Leino and Tapio Salakoski},
title = {Turku Neural Parser Pipeline: An End-to-End System for the CoNLL 2018 Shared Task},
booktitle = {Proceedings of the CoNLL 2018 Shared Task: Multilingual Parsing from Raw Text to Universal Dependencies},
publisher = "Association for Computational Linguistics",
location = "Brussels, Belgium",
year={2018}
}
```

Other references TODO
