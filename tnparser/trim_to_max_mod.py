import sys
import io
import argparse
import transformers
import json

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

def restrict_tokens(sent,comments,cache,args):
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

def restrict_subwords(sent,comments,cache,args,bert_tokenizer):
    subw_lengths=0
    for i,token in enumerate(sent):
        token_sub=bert_tokenizer.tokenize(token[FORM])
        if len(token_sub)>args.max_token_len:
            comments.append("###TOKEN {tid} TRIMMED_BY_PARSER FROM ORIGINAL OF {l} SUBWORDS | ORIG_TOKEN={orig}".format(tid=str(i+1), l=len(token_sub), orig=token[FORM]))
            sent[i][FORM]=bert_tokenizer.convert_tokens_to_string(token_sub[:args.max_token_len])
        N=min(len(token_sub),args.max_token_len)
        if subw_lengths+N>args.max_sent_len: #adding this token would push me over the limit!
            comments.append("###TRIMMED_BY_PARSER FROM ORIGINAL OF {} WORDS".format(len(sent)))
            sent=sent[:i]
            break
        subw_lengths+=N
    if comments:
        print("\n".join(comments),file=cache)
    for cols in sent:
        for col in (LEMMA,UPOS,XPOS,FEATS,HEAD,DEPREL,DEPS):
            cols[col]="_"
        print("\t".join(cols),file=cache)
    print(file=cache)

            
def launch(args,q_in,q_out):
    if args.udify_config is not None:
        with open(args.udify_config) as f:
            udf_cfg=json.load(f)
            bertmodel=udf_cfg["dataset_reader"]["token_indexers"]["bert"]
            assert bertmodel["type"]=="udify-bert-pretrained"
            bert_pretrained_model_name=bertmodel["pretrained_model"]
        bert_tokenizer=transformers.BertTokenizer.from_pretrained(bert_pretrained_model_name)
    else:
        bert_tokenizer=None
    while True:
        jobid,txt=q_in.get()
        if jobid=="FINAL":
            q_out.put((jobid,txt))
            return
        cache=io.StringIO()
        for sent,comments in read_conll(txt.split("\n"),drop_tokens=False,drop_nulls=False):
            if bert_tokenizer is not None:
                restrict_subwords(sent,comments,cache,args,bert_tokenizer)
            else:
                restrict_tokens(sent,comments,cache,args)
        q_out.put((jobid,cache.getvalue()))
    
argparser = argparse.ArgumentParser(description='Trims sentence to a max length, protection against super-rare memory errors')
argparser.add_argument('--max_sent_len', default=100,type=int, help='Maximum sentence length. Default: %(default)d')
argparser.add_argument('--max_token_len', default=100,type=int, help='Maximum token length. Default: %(default)d')
argparser.add_argument('--udify-config', default=None, help='If given, BERT tokenizer will be loaded and used to restrict sequence lengths. If given, the max_sent_len and max_token_len will be interpreted in terms of BERT subwords.')



