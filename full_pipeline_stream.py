from pipeline import Pipeline
import sys
import select
import threading
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

def blocking_batch(inp,batch_lines=10000,wait_for_empty_line=False):
    line_buffer=[]
    while True:
        print("Waiting for next line",file=sys.stderr,flush=True)
        line=inp.readline()
        print("Line",repr(line),file=sys.stderr,flush=True)
        if not line: #EOF
            if line_buffer:
                print("Yielding on EOF",file=sys.stderr,flush=True)
                yield "".join(line_buffer)
            print("Done batching",file=sys.stderr,flush=True)
            return
        line_buffer.append(line)
        if (line.strip()=="" or not wait_for_empty_line) and len(line_buffer)>batch_lines:
            print("Yielding",file=sys.stderr,flush=True)
            yield "".join(line_buffer)
            line_buffer=[]

def output_thread(p,out,verbose=False):
    started=time.time()
    next_report=started+5.0
    total_trees_parsed=0
    while True:
        parsed=p.get(None)
        if verbose:
            tree_count=sum(1 for line in parsed.split("\n") if line.startswith("1\t"))
            total_trees_parsed+=tree_count
            if time.time()>next_report:
                print("\n\n************************\n\n",file=sys.stderr,flush=True)
                duration=time.time()-started
                print("{} [trees]   {}:{} [min:sec]   {} [trees/sec]   {} [sec/tree]".format(total_trees_parsed,duration//60,int(duration)%60,total_trees_parsed/duration,duration/total_trees_parsed),file=sys.stderr,flush=True)
                print("\n\n************************\n\n",file=sys.stderr,flush=True)
                next_report=time.time()+5.0
        print(parsed,end="",flush=True,file=out)
        if p.input_finished and p.job_counter==0:
            break
        

if __name__=="__main__":
    import argparse
    THISDIR=os.path.dirname(os.path.abspath(__file__))
    argparser = argparse.ArgumentParser(description='Parser pipeline')
    argparser.add_argument('--conf-yaml', default=os.path.join(THISDIR,"pipelines.yaml"), help='YAML with pipeline configs. Default: parser_dir/pipelines.yaml')
    argparser.add_argument('--pipeline', default="fi_tdt_all", help='Name of the pipeline to run, one of those given in the YAML file. Default: %(default)s')
    argparser.add_argument('--empty-line-batching', default=False, action="store_true", help='Only ever batch on newlines (useful with pipelines that input conllu)')
    argparser.add_argument('--batch-lines', default=10000, help='Number of lines in a job batch. Default %(default)d')
    argparser.add_argument('--blocking-read', default=None, help='Use blocking read instead of non-blocking, give a filename (can be gzip)')
    args = argparser.parse_args()

    with open(args.conf_yaml) as f:
        pipelines=yaml.load(f)

    
    p=Pipeline(steps=pipelines[args.pipeline])
    p.input_finished=False


    #Fetch results from pipeline in an infinite loop
    outp_t=threading.Thread(target=output_thread,args=(p,sys.stdout,True))
    outp_t.start()
    
    time.sleep(3)

    if args.blocking_read:
        fname=args.blocking_read
        print("Blocking batches from",fname,file=sys.stderr,flush=True)
        if fname.endswith(".gz"):
            f=gzip.open(fname,"rt")
        else:
            f=open(fname)
        print("Preparing blocking batches",fname,f,file=sys.stderr,flush=True)
        batches=blocking_batch(f,batch_lines=args.batch_lines,wait_for_empty_line=args.empty_line_batching)
        print("Starting input batching (blocking)...",batches,file=sys.stderr,flush=True)
    else:
        print("Preparing nonblocking batches",fname,f,file=sys.stderr,flush=True)
        batches=non_blocking_batch(sys.stdin,batch_lines=args.batch_lines,wait_for_empty_line=args.empty_line_batching)
        print("Starting input batching (non-blocking)...",file=sys.stderr,flush=True)
    for batch in batches:
        print("\n\nSubmitting a batch of ",batch.count("\n"),"lines\n\n",file=sys.stderr,flush=True)
        p.put(batch)
        assert outp_t.is_alive()
    p.input_finished=True
    outp_t.join() #wait till output done

    #...and we're done

    
