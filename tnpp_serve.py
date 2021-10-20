#!/usr/bin/env python
import yaml
import os
import flask
import sys
from tnparser.pipeline import Pipeline, read_pipelines

app=flask.Flask(__name__)
model=os.environ.get("TNPP_MODEL","models_fi_tdt/pipelines.yaml")
pipeline=os.environ.get("TNPP_PIPELINE","parse_plaintext")
max_char=int(os.environ.get("TNPP_MAX_CHARS",15000))
available_pipelines=read_pipelines(model)
p=Pipeline(available_pipelines[pipeline])
             
@app.route("/",methods=["GET"])
def parse_get():
    global p
    txt=flask.request.args.get("text")
    if not txt:
        return "You need to specify ?text=sometext",400
    res=p.parse(txt)
    return flask.Response(res,mimetype="text/plain; charset=utf-8")

@app.route("/",methods=["POST"])
def parse_post():
    global p,max_char
    txt=flask.request.get_data(as_text=True)
    if max_char>0:
        txt=txt[:max_char]
    if not txt:
        return """You need to post your data as a single string. An example request would be curl --request POST --data 'Tämä on testilause' http://localhost:7689\n\n\n""",400
    else:
        res=p.parse(txt)
    return flask.Response(res,mimetype="text/plain; charset=utf-8")


