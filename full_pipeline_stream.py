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
        pipelines=yaml.load(f, Loader=yaml.BaseLoader)
    for pipeline_name,component_list in pipelines.items():
        new_component_list=[c.format(thisdir=absdir) for c in component_list]
        pipelines[pipeline_name]=new_component_list
    return pipelines
            
if __name__=="__main__":
    import argparse
    THISDIR=os.path.dirname(os.path.abspath(__file__))

    argparser = argparse.ArgumentParser(description='Parser pipeline')
    general_group = argparser.add_argument_group(title='General', description='General pipeline arguments')
    general_group.add_argument('--conf-yaml', default=os.path.join(THISDIR,"pipelines.yaml"), help='YAML with pipeline configs. Default: parser_dir/pipelines.yaml')
    general_group.add_argument('--pipeline', default="parse_plaintext", help='[DEPRECATED] Name of the pipeline to run, one of those given in the YAML file. Default: %(default)s')
    general_group.add_argument('--empty-line-batching', default=False, action="store_true", help='Only ever batch on newlines (useful with pipelines that input conllu)')
    general_group.add_argument('--batch-lines', default=1000, type=int, help='Number of lines in a job batch. Default %(default)d, consider setting a higher value if using conllu input instead of raw text (maybe 5000 lines), and try smaller values in case of running out of memory with raw text.')
    general_group.add_argument('action', default=None, nargs='?', help="What to do. Either 'list' to lists pipelines or a pipeline name to parse, or nothing in which case the default parse_plaintext is used.")

    lemmatizer_group = argparser.add_argument_group(title='lemmatizer_mod', description='Lemmatizer arguments')
    lemmatizer_group.add_argument('--gpu', dest='lemmatizer_mod.gpu', type=int, default=0, help='GPU device id for the lemmatizer, if -1 use CPU')
    lemmatizer_group.add_argument('--batch_size', dest='lemmatizer_mod.batch_size', type=int, default=100, help='Lemmatizer batch size')


    args = argparser.parse_args()


    pipelines=read_pipelines(args.conf_yaml)

    if args.action=="list":
        print(sorted(pipelines.keys()),file=sys.stderr,flush=True)
        sys.exit(0)
    elif args.action is not None and args.action!="parse": #deprecated legacy stuff, allowing calls like --pipeline pipelinename parse
        pipeline=pipelines[args.action]
    elif args.action is None or args.action=="parse":
        pipeline=pipelines[args.pipeline]
        
    if pipeline[0].startswith("extraoptions"):
        extraoptions=pipeline[0].split()[1:]
        pipeline.pop(0)
        newoptions=extraoptions+sys.argv[1:]
        print("Got extra arguments from the pipeline, now running with", newoptions, file=sys.stderr, flush=True)
        args=argparser.parse_args(newoptions)

    pipeline.append("output_mod")
    p=Pipeline(steps=pipeline, extra_args=args)

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
            if not p.is_alive(): #gotta end if something dies
                print("Something crashed. Exiting.",file=sys.stderr,flush=True)
                sys.exit(-1)
            print("Feeding final batch",file=sys.stderr,flush=True)
            p.put("".join(line_buffer))

    p.send_final()
    p.join()

