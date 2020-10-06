import sys
import io
import argparse
import time
import re
import traceback

ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC = range(10)

def launch(args, q_in, q_out):
    while True:
        jobid,txt=q_in.get()
        if jobid=="FINAL":
            q_out.put((jobid,txt))
            return
        try:
            conllu=parse_text(txt)
            q_out.put((jobid,conllu))
        except:
            traceback.print_exc()
            sys.stderr.flush()
    
def parse_text(txt):
    lines = []
    for line in txt.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            lines.append(line)
        else:
            cols = line.split("\t")
            cols[LEMMA] = "_"
            lines.append("\t".join(cols))
            
    return "\n".join(lines)
    
argparser = argparse.ArgumentParser(description='writer as a process')




