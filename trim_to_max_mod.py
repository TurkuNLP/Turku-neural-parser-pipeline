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
            if len(sent)>args.max_sent_len:
                comments.append("###TRIMMED_BY_PARSER FROM ORIGINAL OF {} WORDS".format(len(sent)))
                sent=sent[:args.max_sent_len]
            for i,token in enumerate(sent):
                if len(token[FORM])>args.max_token_len:
                    comments.append("###TOKEN {tid} TRIMMED_BY_PARSER FROM ORIGINAL OF {l} CHARACTERS | ORIG_TOKEN={orig}".format(tid=str(i+1), l=len(token[FORM]), orig=token[FORM]))
                    sent[i][FORM]=token[FORM][:args.max_token_len]
            if comments:
                print("\n".join(comments),file=cache)
            for cols in sent:
                for col in (LEMMA,UPOS,XPOS,FEATS,HEAD,DEPREL,DEPS):
                    cols[col]="_"
                print("\t".join(cols),file=cache)
            print(file=cache)
        q_out.put((jobid,cache.getvalue()))
    
argparser = argparse.ArgumentParser(description='Trims sentence to a max length, protection against super-rare memory errors')
argparser.add_argument('--max_sent_len', default=100,type=int, help='Maximum sentence length. Default: %(default)d')
argparser.add_argument('--max_token_len', default=100,type=int, help='Maximum token length. Default: %(default)d')


