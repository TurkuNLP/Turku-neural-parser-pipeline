import sys
import transformers
import itertools
import argparse

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
        if len(token_tokenized)>max_seq_len: #we have a problem, the token itself is too long
            #print(f"LONGT >>>>{repr(sent_row[FORM])}<<<<<<<",file=sys.stderr,flush=True)
            for chunk in grouper(sent_row[FORM],max_seq_len,""): #cut the token into individual "sentences"
                new_sentences.append([["1","".join(chunk)]+["_"]*8])
            counter=0
            continue
        if "-" in sent_row[ID]:
            #Now we need to make sure we still fit with all parts
            if counter+len(token_tokenized)*2>max_seq_len:
                new_sentences.append([])
                counter=0
            new_sentences[-1].append(sent_row)
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
    return new_sentences

argparser = argparse.ArgumentParser()
argparser.add_argument("--vocabfile", help="Vocab file of the BERT model to use")
argparser.add_argument("--max-seq-len", type=int, default=500, help="Max seq length to use, default %(default)d")
argparser.add_argument("--merge", action="store_true", help="Undo the transform. Without this parameter, it will run the transform, splitting sentences to max-seq-len pieces")

