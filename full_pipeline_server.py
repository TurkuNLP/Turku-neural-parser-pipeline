import yaml
import os
import flask
import sys
from tnparser.pipeline import Pipeline, read_pipelines
#from full_pipeline_stream import read_pipelines

app=flask.Flask(__name__)

@app.route("/",methods=["GET"])
def parse_get():
    global p, args
    txt=flask.request.args.get("text")
    if not txt:
        return "You need to specify ?text=sometext",400
    res=parse(txt,p)
    return flask.Response(res,mimetype="text/plain; charset=utf-8")

@app.route("/",methods=["POST"])
def parse_post():
    global p,args
    txt=flask.request.get_data(as_text=True)
    if args.max_char>0:
        txt=txt[:args.max_char]
    if not txt:
        return """You need to post your data as a single string. An example request would be curl --request POST --data 'Tämä on testilause' http://localhost:7689\n\n\n""",400
    else:
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

if __name__=="__main__":
    import argparse
    THISDIR=os.path.dirname(os.path.abspath(__file__))

    argparser = argparse.ArgumentParser(description='Parser pipeline')
    general_group = argparser.add_argument_group(title='General', description='General pipeline arguments')
    general_group.add_argument('--conf-yaml', default=os.path.join(THISDIR,"pipelines.yaml"), help='YAML with pipeline configs. Default: parser_dir/pipelines.yaml')
    general_group.add_argument('--empty-line-batching', default=False, action="store_true", help='Only ever batch on newlines (useful with pipelines that input conllu)')
    general_group.add_argument('--batch-lines', default=1000, type=int, help='Number of lines in a job batch. Default %(default)d, consider setting a higher value if using conllu input instead of raw text (maybe 5000 lines), and try smaller values in case of running out of memory with raw text.')
    general_group.add_argument('action', default=None, nargs='?', help="What to do. Either 'list' to lists pipelines or a pipeline name to parse, or nothing in which case the default parse_plaintext is used.")
    general_group.add_argument('--port',default=7689,type=int,help="Port at which to run. Default %(default)d")
    general_group.add_argument('--host',default="localhost",help="Host on which to bind. Default %(default)s")
    general_group.add_argument('--max-char', default=0, type=int, help='Number of chars maximum in a job batch. Cuts longer. Zero for no limit. Default %(default)d')
    
    lemmatizer_group = argparser.add_argument_group(title='lemmatizer_mod', description='Lemmatizer arguments')
    lemmatizer_group.add_argument('--gpu', dest='lemmatizer_mod.gpu', type=int, default=0, help='GPU device id for the lemmatizer, if -1 use CPU')
    lemmatizer_group.add_argument('--batch_size', dest='lemmatizer_mod.batch_size', type=int, default=100, help='Lemmatizer batch size')

    args = argparser.parse_args()

    pipelines = read_pipelines(args.conf_yaml)

    if args.action=="list":
        print(sorted(pipelines.keys()),file=sys.stderr,flush=True)
        sys.exit(0)
    else:
        pipeline=pipelines[args.action]

    if pipeline[0].startswith("extraoptions"):
        extraoptions=pipeline[0].split()[1:]
        pipeline.pop(0)
        newoptions=extraoptions+sys.argv[1:]
        print("Got extra arguments from the pipeline, now running with", newoptions, file=sys.stderr, flush=True)
        args=argparser.parse_args(newoptions)

    p=Pipeline(steps=pipeline, extra_args=args)

    app.run(host=args.host,port=args.port,threaded=True,processes=1,use_reloader=False)
            
            
        
