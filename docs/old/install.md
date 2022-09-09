---
layout: default
---

# Installation

## Prerequisites

For Ubuntu-based systems, the pre-requisities are

    sudo apt install build-essential python3-dev python3-virtualenv python3-tk

## Download the code

Clone the parser as well as all of its submodules as follows:

    git clone https://github.com/TurkuNLP/Turku-neural-parser-pipeline.git
    cd Turku-neural-parser-pipeline
    git checkout orig-parser-pre-2021
    git submodule update --init --recursive

## Setup Python environment

We highly recommend that you make a virtual environment for the parser and install the `wheel` package:

    python3 -m venv venv-parser-neural
    source venv-parser-neural/bin/activate
    pip3 install wheel

Then you need to install the necessary libraries (note: remember to remove tensorflow or pytorch from the requirements if you need to install them separately due to particular limitations of your machine):

    pip3 install -r requirements-gpu.txt

or
   
    pip3 install -r requirements-cpu.txt
    
After downloading a model, you should be able to run the parser.

## Tensorflow and pytorch

In case default versions of Tensorflow or Pytorch do not match your CUDA installation, it makes sense to install those packages separately.

You can install an older or newer version of tensorflow by specifying the version number when running pip (parser is tested to work at least with 1.5.0 -- 1.12.2):

    pip3 install tensorflow-gpu==1.12.2

In case pytorch would not install correctly through pip, you may need to install PyTorch by selecting the appropriate options from https://pytorch.org/. For a typical
GPU install you would select something like "Linux - pip - 3.5 - CUDA 9.1" matching the version of your python and CUDA. If you run on CPU and have no CUDA, then select None.

1. Run the `commands which pytorch.org gives`
2. Run yet `pip3 install torchtext` when (1) is ready and you're done

## Download the models

All models are available [here](http://epsilon-it.utu.fi/dep-parser-models/) and you can use the following utility script to fetch the model you need:

    python3 fetch_models.py fi_tdt

## Test the model

Now you can [test the model](index.md#running-the-parser--short-version)
