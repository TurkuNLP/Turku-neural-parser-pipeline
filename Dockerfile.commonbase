# Base parser install with no models
# This is only needed for building the common base image which is accessible at
# https://hub.docker.com/r/turkunlp/turku-neural-parser
#
# in other words standard users shouldn't need this one
#

FROM python:3.6 as tnpp_base_cpu
WORKDIR /app
COPY requirements-cpu.txt ./
RUN pip3 install --no-cache-dir -r requirements-cpu.txt
COPY *.py *.sh ./
COPY Parser-v2 ./Parser-v2
COPY tokenizer ./tokenizer
COPY universal-lemmatizer ./universal-lemmatizer
