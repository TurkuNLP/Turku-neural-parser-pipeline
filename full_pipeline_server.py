from multiprocessing import Process,Queue
import importlib
import yaml
import os
import flask
import hashlib
import random
import time

class Pipeline:

    def __init__(self,steps):
        """ """
        self.job_counter=0
        self.done_jobs={}
        self.max_q_size=10
        self.q_in=Queue(self.max_q_size) #where to send data to the whole pipeline
        self.q_out=self.q_in #where to receive data from the whole pipeline

        for mod_name_and_params in steps:
            self.add_step(mod_name_and_params)

    
    def add_step(self,module_name_and_params):
        config=module_name_and_params.split()
        module_name=config[0]
        params=config[1:]
        mod=importlib.import_module(module_name)
        step_in=self.q_out
        self.q_out=Queue(self.max_q_size) #new pipeline end
        args=mod.argparser.parse_args(params)
        process=Process(target=mod.launch,args=(args,step_in,self.q_out))
        process.start()

    def put(self,txt):
        """Start parsing a job, return id which can be used to retrieve the result"""
        batch_id=hashlib.md5((str(random.random())+txt).encode("utf-8")).hexdigest()
        self.q_in.put((batch_id,txt)) #first job of 1 total
        self.job_counter+=1
        return batch_id

    def get(self,batch_id):
        if batch_id is None: #get any next batch, don't care about batch_id
            _,finished=self.q_out.get()
            self.job_counter-=1
            return finished
        elif batch_id in self.done_jobs:
            self.job_counter-=1
            return self.done_jobs.pop(batch_id)
        else:
            #get the next job, maybe it's the one?
            finished_id,finished=self.q_out.get()
            if finished_id==batch_id:
                self.job_counter-=1
                return finished
            else: #something got done, but it's not the right one
                self.done_jobs[finished_id]=finished
                return None #whoever asked will have to ask again


if __name__=="__main__":            
    app=flask.Flask(__name__)

    @app.route("/",methods=["GET"])
    def parse_get():
        global b
        txt=flask.request.args.get("text")
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
    argparser.add_argument('ACTION', default="serve", help='`serve` to open http server, `interactive` goes interactive mode. Default: %(default)s')
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
            
            
        
