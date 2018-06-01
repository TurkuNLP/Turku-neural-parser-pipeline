from full_pipeline_server import Pipeline
import sys
import select
import threading
import os
import yaml
import time

def non_blocking_batch(inp,timeout=0.2,batch_lines=10000,wait_for_empty_line=False):
    line_buffer=[]
    #Feeds input
    while True:
        ready_to_read=select.select([inp], [], [], timeout)[0] #check whether f is ready to be read, wait at least timeout (otherwise we run a crazy fast loop)
        if not ready_to_read:
            # Stdin is not ready, yield what we've got, if anything
            if line_buffer:
                #print("Yielding",len(list(line for line in line_buffer if line.startswith("1\t"))), file=sys.stderr)
                #sys.stderr.flush()
                yield "".join(line_buffer)
                line_buffer=[]
            continue #next try
        
        # inp is ready to read!
        # we should always try to get stuff until the next empty line - we might be parsing text paragraphs
        while True:
            line=inp.readline()
            if not line: #End of file detected
                if line_buffer:
                    yield "".join(line_buffer)
                    return
            line_buffer.append(line)
            if not line.strip(): #empty line
                break #our chance to yield
            if not wait_for_empty_line and len(line_buffer)>batch_lines: #okay, we just have to yield
                break

        # Now we got the next sentence --- do we have enough to yield?
        if len(line_buffer)>batch_lines:
            yield "".join(line_buffer) #got enough
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
    args = argparser.parse_args()

    with open(args.conf_yaml) as f:
        pipelines=yaml.load(f)

    
    p=Pipeline(steps=pipelines[args.pipeline])
    p.input_finished=False


    #Fetch results from pipeline in an infinite loop
    outp_t=threading.Thread(target=output_thread,args=(p,sys.stdout,True))
    outp_t.start()

    for batch in non_blocking_batch(sys.stdin,wait_for_empty_line=args.empty_line_batching):
        p.put(batch)
        assert outp_t.is_alive()
    p.input_finished=True
    outp_t.join() #wait till output done

    #...and we're done

    
