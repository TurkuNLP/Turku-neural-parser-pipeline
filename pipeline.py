from multiprocessing import Process,Queue
import importlib
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
        self.processes=[]

        steps.append("output_mod")

        for mod_name_and_params in steps:
            self.add_step(mod_name_and_params)

    def join(self):
        for p in self.processes:
            p.join()

    def is_alive(self):
        for p in self.processes:
            if not p.is_alive():
                return False
        return True

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

