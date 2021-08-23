---
layout: default
---

# Turku neural parser pipeline

A neural parsing pipeline for **segmentation, morphological tagging, dependency parsing and lemmatization with pre-trained models for more than 50 languages**. The pipeline ranked **1st on lemmatization, and 2nd on both LAS and MLAS** (morphology-aware LAS) on the CoNLL-18 Shared Task on Parsing Universal Dependencies. Accuracies for all languages, see TurkuNLP at <https://universaldependencies.org/conll18/results.html>. The pipeline has been improved upon since this shared task (latest **major overhaul in June 2021**)

Looking for the **old version** of the parser (prior to August 2021)? The code is TODO and the old documentation is [linked here](old/index.html).

<div class="latest" markdown="1">
LATEST:

**June, 2021**: **Complete overhaul** 1) restructured as a python package, 2) Udify replaced with diaparser, 3) new tagger; A lot more sane requirements.txt. Old version of this page with all documentation is [here](old/index.html).
    
</div>

## Models

The current pipeline is fully neural and has a substantially better accuracy in all layers of annotation, compared to the old Finnish-dep-parser, used by many. The models are based on the BERT Transformer model. The list of models is [published here](models.html).

# Installation

## From sources

```
git clone https://github.com/TurkuNLP/Turku-neural-parser-pipeline.git
cd Turku-neural-parser-pipeline
python3 -m venv venv-tnpp
source venv-tnpp/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade setuptools
python3 -m pip install -r requirements.txt
```

# Running the parser

## Download a model

The models are simple tar.gz archives, you can either download one using the simple script distributed with the parser

    python3 fetch_models.py fi_tdt_dia

or you can simply download and unzip the model file linked from the [models list](models.html) yourself.

## Running on Google Colab

This is an easy way to run the parser with GPU acceleration. Please see the Colab Notebook [here](https://github.com/TurkuNLP/Turku-neural-parser-pipeline/blob/master/docs/tnpp_diaparse.ipynb) or [open it directly on Google Colab](https://colab.research.google.com/github/TurkuNLP/Turku-neural-parser-pipeline/blob/master/docs/tnpp_diaparse.ipynb).

## Running on command line, just give me the command

In the basic streaming mode `tnpp_parse.py`, the parser reads from stdin, outputs to stdout. You need to give it a file with pipelines (distributed together with each model), and you need to tell it which pipeline to run (parse_plaintext for running segmentation, tagging, syntax and lemmatization; parse_conllu for running tagger, syntax and lemmatization for presegmented conllu-file). So after downloading a model, you can run the parser as:

    #remember to fetch model if you have not done so yet
    echo "Minulla on koira." | python3 tnpp_parse.py --conf models_fi_tdt/pipelines.yaml parse_plaintext

Of course note that there is a nontrival time needed to load the models into memory, so you should avoid repeatedly restarting the parser when parsing longer collections of text.

## Running on command line, more detailed introduction

The parser has these properties:

* a start-up cost when it's loading the models (see the server mode to prevent model reloading)
* very fast when parsing large documents because of the mini-batch style of computing
* transparent handling of metadata

### Input and Output formats

When running with default mode (`parse_plaintext`) the input must be **utf-8** encoded plain text. Paragraph and document boundaries should be marked with an empty line (note that single line break does not indicate text boundary, and lines separated with a single line break can be merged by the tokenizer).

The output format of the parser is CoNLL-U, described in detail [here](https://universaldependencies.org/format.html).

### Metadata in input

In the input data, all lines which start with `###C:` are treated as metadata and will be passed through the pipeline unmodified, and attached in the conllu output to the following sentence. This is an easy way to pass metadata through the pipeline, also through tokenizer and sentence splitting. This is especially useful for example including any document level information (document boundaries, source url, timestamps etc.). Note that since the conllu format attaches metadata to sentences, the last line of a file cannot be the `###C:` comment. It is fine to have several comment lines one after another.

### Pipelines

Various pipelines can be built out of the components of the parser and these are generally defined in model_directory/pipelines.yaml. You can also list what you have like so:

    python3 tnpp_parse.py --conf models_fi_tdt_dia/pipelines.yaml list

For Finnish these are:

* `parse_plaintext` read plain text, tokenize, split into sentences, tag, parse, lemmatize
* `parse_sentlines` read text one sentence per line, tokenize, tag, parse, lemmatize
* `parse_wslines` read whitespace tokenized text one sentence per line, tag, parse, lemmatize
* `parse_conllu` read conllu, wipe existing values from all columns, tag, parse, lemmatize
* `parse_conllu_nolemmas` read conllu, wipe existing values from all columns, tag, parse
* `tokenize` read plain text, tokenize, split into sentences

Other pipelines (which skip some of these steps etc) can be built easily by mimicking the existing pipelines in the `pipelines.yaml` (also see below). If you wish to run conllu input without wipe_mod (which wipes existing values from all columns), note that lemmatizer modules are designed to pass existing lemma values through unchanged and lemmatize only words with empty lemma field (`_`).

### Stream mode

In the stream mode `tnpp_parse.py`, the parser reads from stdin, outputs to stdout. You need to give it the file with pipelines and you need to tell it which pipeline to run (parse_plaintext is the default). So you can run the parser as:

    cat myfile.txt | python3 tnpp_parse.py --conf models_fi_tdt_dia/pipelines.yaml parse_plaintext > myfile.conllu

### Server mode

In the server mode, the parsing models are loaded only once, and kept in memory as long as the server is running. Start the server by running the following command. Arguments (such as the model and pipeline) are passed to the process through environment variables:

    export TNPP_MODEL=models_fi_tdt_dia/pipelines.yaml
    export TNPP_PIPELINE=parse_plaintext
    export TNPP_PORT=7689
    export TNPP_MAX_CHARS=15000 # cut-off on character count to parse; protects from too large requests from web
    export FLASK_APP=tnpp_serve
    flask run -host 0.0.0.0 --port $TNPP_PORT

When the server is running, you can parse data with curl requests:

    curl --request POST --header 'Content-Type: text/plain; charset=utf-8' --data-binary "Tämä on esimerkkilause" http://localhost:7689

### pipelines.yaml file

For those who wish to hack the pipelines.yaml file. You can add `extraoptions` to enforce some parameters applied as if you gave them on the command line. This is curently only used to enforce batching on empty lines in pipelines that parse conllu, making sure the input is not cut in the middle of the line. As you can probably figure out, the pipeline simply specifies which modules are launched and their parameters, new steps to the pipeline are easy to add by mimicking the `*_mod.py` files.

# Speed

**GPU:** The throughput of the full pipeline is on the order of 100 trees/sec In the beginning the reported time looks worse as it includes also model loading

**CPU:** 

# References

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
Lemmatizer:
```
@article{kanerva2020lemmatizer,
title={Universal Lemmatizer: A Sequence to Sequence Model for Lemmatizing Universal Dependencies Treebanks},
author={Kanerva, Jenna and Ginter, Filip and Salakoski, Tapio},
year={2020},
journal={Natural Language Engineering},
publisher={Cambridge University Press},
DOI={10.1017/S1351324920000224},
pages={1--30},
url={http://dx.doi.org/10.1017/S1351324920000224}
}
```



