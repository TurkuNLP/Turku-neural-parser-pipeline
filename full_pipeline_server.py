import yaml
import os
import flask

from pipeline import Pipeline

app=flask.Flask(__name__)

@app.route("/",methods=["GET"])
def parse_get():
    global p
    txt=flask.request.args.get("text")
    if not txt:
        return "You need to specify ?text=sometext",400
    res=parse(txt,p)
    return flask.Response(res,mimetype="text/plain; charset=utf-8")


def parse(txt,p):
    job_id=p.put(txt)
    while True:
        res=p.get(job_id)
        if res is None:
            time.sleep(0.1)
        else:
            break
    return res


import argparse
THISDIR=os.path.dirname(os.path.abspath(__file__))
argparser = argparse.ArgumentParser(description='Parser pipeline')
argparser.add_argument('--conf-yaml', default=os.path.join(THISDIR,"pipelines.yaml"), help='YAML with pipeline configs. Default: parser_dir/pipelines.yaml')
argparser.add_argument('--pipeline', default="fi_tdt_all", help='Name of the pipeline to run, one of those given in the YAML file. Default: %(default)s')
argparser.add_argument('ACTION', default=None, nargs="?", help='`serve` to open http server, `interactive` goes interactive mode. Default: do nothing and exit')
args = argparser.parse_args()

with open(args.conf_yaml) as f:
    pipelines=yaml.load(f)

p=Pipeline(steps=pipelines[args.pipeline])

if args.ACTION=="serve":
    app.run(host="localhost",port=7689,threaded=True,processes=1,use_reloader=False)
elif args.ACTION=="interactive":
    try:
        import readline
    except:
        pass
    while True:
        txt=input("> ")
        print(parse(txt,p),end="")
            
            
        
