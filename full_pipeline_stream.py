from pipeline import Pipeline
import sys
import select
import os
import yaml
import time
import gzip

def non_blocking_batch(inp,timeout=0.2,batch_lines=10000,wait_for_empty_line=False):
    line_buffer=[]
    #Feeds input
    while True:
        ready_to_read=select.select([inp], [], [], timeout)[0] #check whether f is ready to be read, wait at least timeout (otherwise we run a crazy fast loop)
        if not ready_to_read:
            # Stdin is not ready, yield what we've got, if anything
            if line_buffer:
                print("Yielding on timeout",len(line_buffer),"lines",file=sys.stderr,flush=True)
                yield "".join(line_buffer)
                line_buffer=[]
            continue #next try
        
        # inp is ready to read!
        # we should always try to get stuff until the next empty line - we might be parsing text paragraphs
        while True:
            line=inp.readline()
            if not line: #End of file detected
                if line_buffer:
                    print("Yielding on end-of-input",len(line_buffer),"lines",file=sys.stderr,flush=True)
                    yield "".join(line_buffer)
                print("End-of-file detected",file=sys.stderr,flush=True)
                return
            line_buffer.append(line)
            if not line.strip(): #empty line
                break #our chance to yield
            if not wait_for_empty_line and len(line_buffer)>batch_lines: #okay, we just have to yield
                break

        # Now we got the next sentence --- do we have enough to yield?
        if len(line_buffer)>batch_lines:
            print("Yielding on full batch",len(line_buffer),"lines",file=sys.stderr,flush=True)
            yield "".join(line_buffer) #got enough
            line_buffer=[]

def read_pipelines(fname):
    absdir=os.path.dirname(os.path.abspath(fname))
    with open(fname) as f:
        pipelines=yaml.load(f)
    for pipeline_name,component_list in pipelines.items():
        new_component_list=[c.format(thisdir=absdir) for c in component_list]
        pipelines[pipeline_name]=new_component_list
    return pipelines
            
if __name__=="__main__":
    import argparse
    THISDIR=os.path.dirname(os.path.abspath(__file__))
    argparser = argparse.ArgumentParser(description='Parser pipeline')
    argparser.add_argument('--conf-yaml', default=os.path.join(THISDIR,"pipelines.yaml"), help='YAML with pipeline configs. Default: parser_dir/pipelines.yaml')
    argparser.add_argument('--pipeline', default="fi_tdt_all", help='Name of the pipeline to run, one of those given in the YAML file. Default: %(default)s')
    argparser.add_argument('--empty-line-batching', default=False, action="store_true", help='Only ever batch on newlines (useful with pipelines that input conllu)')
    argparser.add_argument('--batch-lines', default=10000, type=int, help='Number of lines in a job batch. Default %(default)d')
    argparser.add_argument('action', default="parse", nargs='?', help='What to do. parse (parses), list (lists pipelines)')
    args = argparser.parse_args()

    pipelines=read_pipelines(args.conf_yaml)

    if args.action=="list":
        print(sorted(pipelines.keys()),file=sys.stderr,flush=True)
        sys.exit(0)
        
    pipeline=pipelines[args.pipeline]
    if pipeline[0].startswith("extraoptions"):
        extraoptions=pipeline[0].split()[1:]
        pipeline.pop(0)
        newoptions=extraoptions+sys.argv[1:]
        print("Got extra arguments from the pipeline, now running with", newoptions, file=sys.stderr, flush=True)
        args=argparser.parse_args(newoptions)
    p=Pipeline(steps=pipeline)

    print("Waiting for input",file=sys.stderr,flush=True)
    line_buffer=[]
    for line in sys.stdin:
        line_buffer.append(line)
        if (line.strip()=="" or not args.empty_line_batching) and len(line_buffer)>args.batch_lines:
            if not p.is_alive(): #gotta end if something dies
                print("Something crashed. Exiting.",file=sys.stderr,flush=True)
                sys.exit(-1)
            print("Feeding a batch",file=sys.stderr,flush=True)
            p.put("".join(line_buffer))
            line_buffer=[]
    else:
        if line_buffer:
            print("Feeding final batch",file=sys.stderr,flush=True)
            p.put("".join(line_buffer),final=True)

    print("DONE",file=sys.stderr,flush=True)
    p.join()

