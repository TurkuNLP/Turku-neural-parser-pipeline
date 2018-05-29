from multiprocessing import Process,Queue
import importlib

pipelines={"fi_tdt_all":[
    ("tokenizer_server",[]),
    ("parser_server",["--model","models/Finnish-Tagger"]),
    ("parser_server",["--model","models/Finnish-Parser","--process_morpho"]),
    ("lemmatizer_server",["--model", "models/lemmatizer.pt"])]
}

class Pipeline:

    def add_step(self,module_name,params):
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

        for mod_name, params in steps:
            self.add_step(mod_name,params)
        
if __name__=="__main__":
    p=Pipeline(steps=pipelines["fi_tdt_all"])

    while True:
        txt=input("ws-text> ")
        p.q_in.put(txt)
        processed=p.q_out.get()
        print(processed,end="")
        
