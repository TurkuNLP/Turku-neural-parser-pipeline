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
