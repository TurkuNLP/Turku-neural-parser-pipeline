---
layout: default
---

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

## Download the models

All models are available [here](http://dl.turkunlp.org/turku-parser-models/). Models compatible with the present version of the parser have `-dia` in their name. You can use the following utility script to fetch the model you need:

    python3 fetch_models.py fi_tdt_dia

Alternatively, you can simply download and unpack the model file from the page linked above.

## Test the model

Now you can [test the model](index.md#running-the-parser--short-version)
