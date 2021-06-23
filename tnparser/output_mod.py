import sys
import io
import argparse
import time
import re

token_regex=re.compile("[0-9]+\t")

def launch(args,q_in,q_out):
    start=None
    next_report=None
    total_parsed_trees=0
    total_parsed_tokens=0
    while True:
        jobid,txt=q_in.get()
        if jobid=="FINAL":
            print("Output exiting",file=sys.stderr,flush=True)
            return
        print(txt,end="",flush=True)
        if start is None:
            start=time.time()
            next_report=start+10.0 #report every 10sec at most
            print("HITHERE",file=sys.stderr,flush=True)
        else:
            total_parsed_trees+=sum(1 for line in txt.split("\n") if line.startswith("1\t"))
            total_parsed_tokens+=sum(1 for line in txt.split("\n") if re.match(token_regex, line))
            if total_parsed_trees>0 and time.time()>next_report:
                time_spent=time.time()-start
                print("Runtime from beginning: {}:{} [m:s]  Parsed: {} [trees], {} [tokens]  Speed: {} [trees/sec]  {} [sec/tree] {} [tokens/sec]".format(int(time_spent)//60,int(time_spent)%60,total_parsed_trees,total_parsed_tokens, total_parsed_trees/time_spent,time_spent/total_parsed_trees, total_parsed_tokens/time_spent) ,file=sys.stderr,flush=True)
                next_report=time.time()+10

    
argparser = argparse.ArgumentParser(description='writer as a process')




