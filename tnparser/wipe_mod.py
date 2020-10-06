import sys
import io
import argparse

ID,FORM,LEMMA,UPOS,XPOS,FEATS,HEAD,DEPREL,DEPS,MISC=range(10)

def read_conll(inp,max_sent=0,drop_tokens=True,drop_nulls=True):
    comments=[]
    sent=[]
    yielded=0
    for line in inp:
        line=line.strip()
        if line.startswith("#"):
            comments.append(line)
        elif not line:
            if sent:
                yield sent,comments
                yielded+=1
                if max_sent>0 and yielded==max_sent:
                    break
                sent,comments=[],[]
        else:
            cols=line.split("\t")
            if drop_tokens and "-" in cols[ID]:
                continue
            if drop_nulls and "." in cols[ID]:
                continue
            sent.append(cols)
    else:
        if sent:
            yield sent,comments

def launch(args,q_in,q_out):
    while True:
        jobid,txt=q_in.get()
        if jobid=="FINAL":
            q_out.put((jobid,txt))
            return
        cache=io.StringIO()
        for sent,comments in read_conll(txt.split("\n"),drop_tokens=False,drop_nulls=False):
            if comments:
                print("\n".join(comments),file=cache)
            for cols in sent:
                for col in (LEMMA,UPOS,XPOS,FEATS,HEAD,DEPREL,DEPS):
                    cols[col]="_"
                print("\t".join(cols),file=cache)
            print(file=cache)
        q_out.put((jobid,cache.getvalue()))
    
argparser = argparse.ArgumentParser(description='Wipes LEMMA,UPOS,XPOS,FEATS,HEAD,DEPREL,DEPS conllu columns to make sure this is test-grade run, keeps tokens and null words')


