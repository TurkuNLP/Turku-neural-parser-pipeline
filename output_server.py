import sys
import io
import argparse
import time


def launch(args,q_in,q_out):
    start=time.time()
    total_parsed=0
    next_report=start+10.0 #report every 10sec at most
    while True:
        jobid,txt=q_in.get()
        if jobid=="FINAL":
            print("Output exiting",file=sys.stderr,flush=True)
            return
        total_parsed+=sum(1 for line in txt.split("\n") if line.startswith("1\t"))
        if total_parsed>0 and time.time()>next_report:
            time_spent=time.time()-start
            print("Runtime: {}:{} [m:s]  Parsed: {} [trees]  Speed: {} [trees/sec]  {} [sec/tree]".format(int(time_spent)//60,int(time_spent)%60,total_parsed,total_parsed/time_spent,time_spent/total_parsed),file=sys.stderr,flush=True)
            next_report=time.time()+10
        print(txt,end="",flush=True)
    
argparser = argparse.ArgumentParser(description='writer as a process')




