---
layout: default
---

# Turku neural parser pipeline

A neural parsing pipeline for **segmentation, morphological tagging, dependency parsing and lemmatization with pre-trained models for more than 50 languages**. The pipeline ranked **1st on lemmatization, and 2nd on both LAS and MLAS** (morphology-aware LAS) on the CoNLL-18 Shared Task on Parsing Universal Dependencies. Accuracies for all languages, see TurkuNLP at <https://universaldependencies.org/conll18/results.html>.

<div class="latest" markdown="1">
LATEST:

May 27, 2019: **GPU docker images** available. See the [instructions here](docker.html).

Mar 05, 2019: **Server-mode docker images** available for parsing without re-loading the model between requests. See the 
[instructions here](docker.html)

Dec 28, 2018: **Docker images** available. See the [instructions here](docker.html).

Dec 18, 2018: **Finnish model updated** (fi_tdt), should be now faster as it includes a bigger precomputed lemma cache (no changes in accuracy)
    --> run `python3 fetch_models.py fi_tdt` to get the latest

Dec 14, 2018: **Faster lemmatizer**, major updates for the lemmatizer making it considerably faster (no changes in accuracy).
    --> Pipeline needs clean instalation (requirements also changed)!
    
</div>

## Finnish

The current pipeline is fully neural and has a substantially better accuracy in all layers of annotation, compared to the old Finnish-dep-parser, used by many. These are the current numbers for Finnish, measured using the CoNLL18 ST evaluation script on Finnish-TDT UD ver 2.2 data. **This is the "fi_tdt" model distributed with the parser**

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

# Docker Images

The Docker images are an easy way to run the parser without installing all the dependencies. See the instructions [here](docker.html).

# Installation

The installation of the parser, with its dependencies, is described [here](install.html)

# Training

Training new models is described [here](training.html)

# Models

The 82 models for all languages in the CoNLL-18 Shared Task are available for download. Follow the instructions [here](install.html#download-the-models) to download a specific model to a local installation of the parser or [here](docker.html#images-for-other-languages) for the Docker version of the parser.

# Running the parser -- short version

See [here](docker.html) for running the Docker version of the parser.

In the basic streaming mode `full_pipeline_stream.py`, the parser reads from stdin, outputs to stdout. You need to give it a file with pipelines (distributed together with each model), and you need to tell it which pipeline to run (parse_plaintext for running segmentation, tagging, syntax and lemmatization; parse_conllu for running tagger, syntax and lemmatization for presegmented conllu-file). So after downloading a model, you can run the parser as (with GPU lemmatizer):

    echo "Minulla on koira." | python3 full_pipeline_stream.py --conf models_fi_tdt/pipelines.yaml parse_plaintext
    
or (with CPU lemmatizer)

    echo "Minulla on koira." | python3 full_pipeline_stream.py --gpu -1 --conf models_fi_tdt/pipelines.yaml parse_plaintext


# Running the parser -- long version

The parser has these properties:

* a long start-up cost when it's loading the models (see the server mode to prevent model reloading)
* very fast when parsing large documents because of the mini-batch style of computing
* efficient use of GPU, 5x faster than the previous Finnish-dep-parser (which could not use GPU for anything)
* transparent handling of metadata

## Input and Output formats

When running with default mode (`parse_plaintext`) the input must **utf-8** encoded plain text. Paragraph and document boundaries should be marked with an empty line (note that single line break does not indicate text boundary, and lines separated with a single line break can be merged by the tokenizer).

The output format of the parser is CoNLL-U, described in detail [here](https://universaldependencies.org/format.html).

## Metadata in input

In the input data, all lines which start with `###C:` are treated as metadata and will be passed through the pipeline unmodified, and attached in the conllu output to the following sentence. This is an easy way to pass metadata through the pipeline, also through tokenizer and sentence splitting. This is especially useful for example including any document level information (document boundaries, source url, timestamps etc.). Note that since the conllu format attaches metadata to sentences, the last line of a file cannot be the `###C:` comment. It is fine to have several comment lines one after another.

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

    cat myfile.txt | python3 full_pipeline_stream.py --conf models_fi_tdt/pipelines.yaml parse_plaintext > myfile.conllu

## Server mode

See [here](docker.html) for running the Docker version of the parser server.

In the server mode, the parsing models are loaded only once, and kept in memory as long as the server is running. Start the server by running (add `--gpu -1` for CPU inference):
    
    python full_pipeline_server.py --port 7689 --conf models_fi_tdt/pipelines.yaml parse_plaintext

When the server is running, you can parse data with curl requests:

    curl --request POST --header 'Content-Type: text/plain; charset=utf-8' --data-binary "Tämä on esimerkkilause" http://localhost:7689

# pipelines.yaml file

For those who wish to hack the pipelines.yaml file. You can add `extraoptions` to enforce some parameters applied as if you gave them on the command line. This is curently only used to enforce batching on empty lines in pipelines that parse conllu, making sure the input is not cut in the middle of the line. As you can probably figure out, the pipeline simply specifies which modules are launched and their parameters, new steps to the pipeline are easy to add by mimicking the `*_mod.py` files.

# Speed

**GPU:** The throughput of the full pipeline is on the order of 218 trees/sec on NVIDIA GeForce GTX 1070. In the beginning the reported time looks worse as it includes also model loading, the maximum 218 trees/sek is measured after processing 300K sentences (after about 30 min of running).

**CPU:** On my laptop (8 cores + 8GB of RAM) I was able to run approx. 22 trees/sec (measured after processing 20K sentences).

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
@article{kanerva2019universal,
    title={Universal Lemmatizer: A Sequence to Sequence Model for Lemmatizing Universal Dependencies Treebanks},
    author={Jenna Kanerva and Filip Ginter and Tapio Salakoski},
    journal={arXiv preprint arXiv:1902.00972},
    year={2019}
}
```



