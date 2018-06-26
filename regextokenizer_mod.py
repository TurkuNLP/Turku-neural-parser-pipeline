import sys
import io
import argparse
import numpy as np
import pickle
import re

sent_regex=re.compile(r"""[.!?](?=\s+[A-Z]|$)""",re.U|re.M)
#token_regex=re.compile(r"""([,;:")\]]|[.'?!-]+)(?=\b)|(?<=\b)(['"(\[]+)""")
token_regex=re.compile(r"""\s|([,:;']+)(?=[\s]|[.?!]|$)|([.?!]+)(?=$)|(?<=\s)([']+)|(?<=^)([']+)""",re.U|re.M)

def launch(args,q_in,q_out):
    while True:
        jobid,txt=q_in.get()
        if jobid=="FINAL":
            q_out.put((jobid,txt))
            return
        cache=io.StringIO()
        for sent in sentences(txt):
            for id,token in enumerate(tokens(sent)):
                print(id+1,token,*(["_"]*8),sep="\t",file=cache)
            print(file=cache)
        q_out.put((jobid,cache.getvalue()))


def sentences(s):
    sents=[]
    prev=0
    for match in sent_regex.finditer(s):
        sents.append(s[prev:match.end()].strip())
        prev=match.end()
    else:
        if s[prev:]:
            sents.append(s[prev:].strip())
    return sents

def tokens(sent):
    parts=token_regex.split(sent)
    parts=[p for p in parts if p and p.strip()]
    return parts
        

argparser = argparse.ArgumentParser(description='Quick hack regex tokenizer')
if __name__=="__main__":
    inp=sys.stdin.read()
    sents=sentences(inp.strip())
    for s in sents:
        print(s)
        print(*tokens(s))
        print()
        

