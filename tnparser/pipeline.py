from multiprocessing import Process,Queue
import multiprocessing as multiprocessing
import importlib
import hashlib
import random
import time
import os
import yaml
from signal import signal, SIGCHLD
import sys

def read_pipelines(fname):
    absdir=os.path.dirname(os.path.abspath(fname))
    with open(fname) as f:
        pipelines=yaml.load(f, Loader=yaml.BaseLoader)
    for pipeline_name,component_list in pipelines.items():
        new_component_list=[c.format(thisdir=absdir) for c in component_list]
        pipelines[pipeline_name]=new_component_list
    return pipelines

class Pipeline:

    def __init__(self, steps, extra_args=None):
        """ """
        self.ctx=multiprocessing.get_context()
        self.job_counter=0
        self.done_jobs={}
        self.max_q_size=5
        self.q_in=self.ctx.Queue(self.max_q_size) #where to send data to the whole pipeline
        self.q_out=self.q_in #where to receive data from the whole pipeline
        self.modules = []
        self.processes=[]

        for mod_name_and_params in steps:
            self.add_step(mod_name_and_params, extra_args)
        try:
            signal(SIGCHLD, self.handle_sigchld)
        except ValueError:
            print(
                "Warning: could not install SIGCHLD handler. "
                "Pipeline will not terminate if children exit abnormally."
            )

    def handle_sigchld(self, signum, frame):
        while 1:
            pid, exitno = os.waitpid(0, os.WNOHANG)
            if pid == 0:
                return
            if exitno == 0:
                continue
            for module, process in zip(self.modules, self.processes):
                if process.pid != pid:
                    continue
                print(
                    f"Error: pipeline stage died with exit code {exitno}: {module}",
                    file=sys.stderr,
                    flush=True
                )
                sys.exit(-64)

    def join(self):
        for p in self.processes:
            p.join()

    def is_alive(self):
        for p in self.processes:
            if not p.is_alive():
                return False
        return True

    def add_step(self,module_name_and_params, extra_args):
        config=module_name_and_params.split()
        module_name=config[0]
        params=config[1:]

        # collect extra arguments from command line meant for this particular module
        if extra_args is not None: 
            for _name, _value in extra_args.__dict__.items():
                if _name.startswith(module_name):
                    _modname,_argname=_name.split(".",1) # for example lemmatizer_mod.gpu
                    params.append("--"+_argname)
                    params.append(str(_value))

        mod=importlib.import_module("tnparser."+module_name)
        step_in=self.q_out
        self.q_out=self.ctx.Queue(self.max_q_size) #new pipeline end
        args=mod.argparser.parse_args(params)
        process=self.ctx.Process(target=mod.launch,args=(args,step_in,self.q_out))
        process.daemon=True
        process.start()
        self.modules.append(module_name_and_params)
        self.processes.append(process)

    def send_final(self):
        self.q_in.put(("FINAL",""))
        
    def put(self,txt,final=False):
        """Start parsing a job, return id which can be used to retrieve the result"""
        batch_id=hashlib.md5((str(random.random())+txt).encode("utf-8")).hexdigest()
        self.q_in.put((batch_id,txt)) #first job of 1 total
        self.job_counter+=1
        if final:
            self.q_in.put(("FINAL",""))
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

    def parse(self,txt):
        job_id=self.put(txt)
        while True:
            res=self.get(job_id)
            if res is None:
                time.sleep(0.1)
            else:
                break
        return res

    def parse_batched(self,inp,):
        """inp: is a file-like object with input data
           yield_res: 
           """
        pass
           
        
