import sys
import transformers
import itertools
import argparse
import re

ID,FORM,LEMMA,UPOS,XPOS,FEAT,HEAD,DEPREL,DEPS,MISC=range(10)

def read_conllu(txt):
    sent=[]
    comment=[]
    for line in txt.split("\n"):
        line=line.strip()
        if not line: # new sentence
            if sent:
                yield comment,sent
            comment=[]
            sent=[]
        elif line.startswith("#"):
            comment.append(line)
        else: #normal line
            cols=line.split("\t")
            sent.append(cols)
    else:
        if sent:
            yield comment, sent

def format_conllu(sents):
    res=[]
    for comments,sent in sents:
        if comments:
            res.extend(comments)
        res.extend("\t".join(row) for row in sent)
        res.append("")
    return "\n".join(res)+"\n"
            
def launch(args, q_in, q_out):
    if not args.merge:
        tokenizer=transformers.BertTokenizer.from_pretrained(args.vocabfile)
        max_seq_len=args.max_seq_len
        
        while True:
            jobid,txt=q_in.get()
            if jobid=="FINAL":
                q_out.put((jobid,txt))
                return
            split_batch=[]
            for comment,sent in read_conllu(txt):
                split_sents=split(sent,tokenizer,max_seq_len)
                split_batch.append((comment,split_sents[0]))
                for ss in split_sents[1:]:
                    split_batch.append((["### TNPP MERGE INTO PREVIOUS"],ss))
            q_out.put((jobid,format_conllu(split_batch)))
    else:
        #our job is to merge
        while True:
            jobid,txt=q_in.get()
            if jobid=="FINAL":
                q_out.put((jobid,txt))
                return
            new_sents=list(merge(read_conllu(txt)))
            q_out.put((jobid,format_conllu(new_sents)))
                      


        
def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)



def merge(sentences):
    current_comments=[]
    current_sent=None
    for comments,sent in sentences:
        for row in sent:
            if "BERT512TRUNCATEDTOKEN_ORIG=" in row[MISC]:
                match=re.search(r"\|?BERT512TRUNCATEDTOKEN_ORIG=(.*)=GIRO_NEKOT",row[MISC])
                if not match:
                    print("MISC:",row[MISC],file=sys.stderr)
                row[FORM]=match.group(1)
                row[LEMMA]=row[FORM]
                row[MISC]=row[MISC][:match.start()]+row[MISC][match.end():]
                if not row[MISC]:
                    row[MISC]="_"
        if comments==["### TNPP MERGE INTO PREVIOUS"]:
            # this one needs to be merged into previous
            offset=int(current_sent[-1][ID]) #this much needs to be added everywhere
            for row in sent:
                parts=row[ID].split("-")
                parts="-".join((str(int(p)+offset) for p in parts)) #add to everything
                row[ID]=parts
                if row[HEAD]=="0": #join to prev sent last word via dep
                    row[HEAD]=current_sent[-1][ID]
                elif row[HEAD]!="_":
                    row[HEAD]=str(int(row[HEAD])+offset)
                current_sent.append(row)
        else:
            #This is a normal sentence;
            if current_sent:
                yield (current_comments,current_sent)
            current_comments,current_sent=comments,sent
    else:
        if current_sent:
            yield current_comments, current_sent
                
        
def split(sent,tokenizer,max_seq_len):
    new_sentences=[[]]
    text=list(row[FORM] for row in sent) #tokens
    bert_tokenized=[tokenizer.tokenize(t) for t in text]
    counter=0        
    for sent_row, token_tokenized in zip(sent,bert_tokenized):
        if len(token_tokenized)>max_seq_len or len(token_tokenized)==0 or token_tokenized==['[UNK]']: #we have a problem, the token itself is too long or weird in some manner
            if sent_row[MISC]=="_":
                sent_row[MISC]="BERT512TRUNCATEDTOKEN_ORIG="+sent_row[FORM]+"=GIRO_NEKOT"
            else:
                sent_row[MISC]=sent_row[MISC]+"|BERT512TRUNCATEDTOKEN_ORIG="+sent_row[FORM]+"=GIRO_NEKOT"
            sent_row[FORM]=sent_row[FORM][:15]
            if counter+len(sent_row[FORM])>max_seq_len:
                new_sentences.append([])
                counter=0
            counter+=len(sent_row[FORM])
            new_sentences[-1].append(sent_row)
            continue
        if "-" in sent_row[ID]:
            #Now we need to make sure we still fit with all parts
            if counter+len(token_tokenized)*2>max_seq_len:
                new_sentences.append([])
                counter=0
            new_sentences[-1].append(sent_row)
            counter+=len(token_tokenized)
            continue
        if counter+len(token_tokenized)>max_seq_len:
            new_sentences.append([])
            counter=0
        new_sentences[-1].append(sent_row)
        counter+=len(token_tokenized)
    #print(new_sentences)
    #Now make sure all tokens are correctly numbered
    for sent in new_sentences:
        if not sent:
            continue
        first_tok=int(sent[0][ID].split("-")[0])-1 #this much needs to be substracted
        for row in sent:
            parts=row[ID].split("-")
            parts="-".join((str(int(p)-first_tok) for p in parts)) #substract from everything
            row[ID]=parts
            
        # toks=[]
        # for row in sent:
        #     toks.append(tokenizer.tokenize(row[FORM]))
        # if sum(len(t) for t in toks)>512:
        #     print("CRASH",sent,file=sys.stderr)
        #     raise ValueError(sent)
    return new_sentences

argparser = argparse.ArgumentParser()
argparser.add_argument("--vocabfile", help="Vocab file of the BERT model to use")
argparser.add_argument("--max-seq-len", type=int, default=400, help="Max seq length to use, default %(default)d")
argparser.add_argument("--merge", action="store_true", help="Undo the transform. Without this parameter, it will run the transform, splitting sentences to max-seq-len pieces")

