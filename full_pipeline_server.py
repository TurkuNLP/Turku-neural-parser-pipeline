from multiprocessing import Process,Queue
import importlib
import yaml
import os

class Pipeline:

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
    
    def __init__(self,steps):
        """ """
        self.max_q_size=10
        self.q_in=Queue(self.max_q_size) #where to send data to the whole pipeline
        self.q_out=self.q_in #where to receive data from the whole pipeline

        for mod_name_and_params in steps:
            self.add_step(mod_name_and_params)
        
if __name__=="__main__":
    import argparse
    THISDIR=os.path.dirname(os.path.abspath(__file__))
    argparser = argparse.ArgumentParser(description='Parser pipeline')
    argparser.add_argument('--conf-yaml', default=os.path.join(THISDIR,"pipelines.yaml"), help='YAML with pipeline configs. Default: parser_dir/pipelines.yaml')
    argparser.add_argument('--pipeline', default="fi_tdt_all", help='Name of the pipeline to run, one of those given in the YAML file. Default: %(default)s')
    args = argparser.parse_args()

    with open(args.conf_yaml) as f:
        pipelines=yaml.load(f)
    
    p=Pipeline(steps=pipelines[args.pipeline])

    while True:
        txt=input("ws-text> ")
        p.q_in.put(txt)
        processed=p.q_out.get()
        print(processed,end="")
        
