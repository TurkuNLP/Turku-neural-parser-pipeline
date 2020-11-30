import os.path
import sys
import hashlib
import io
import http.server
import urllib
import dummy_handler
import argparse
import re

ID,FORM,LEMMA,UPOS,XPOS,FEAT,HEAD,DEPREL,DEPS,MISC=range(10)

url_regex = re.compile("((https?|ftp)://|www\.)", re.IGNORECASE)
email_regex = re.compile("[^@,:]+@[^@,:]+\.[^@,:]+", re.IGNORECASE)

def read_conllu(f):
    sent=[]
    comment=[]
    for line in f:
        line=line.strip()
        if not line: # new sentence
            if sent:
                yield comment,sent
            comment=[]
            sent=[]
        elif line.startswith("#"):
            comment.append(line)
        else: #normal line
            sent.append(line.split("\t"))
    else:
        if sent:
            yield comment, sent


class LemmaCacheWrapper():

    def __init__(self, args):
        """
        Lemmatizer model loading
        """

        # init lemma cache, comes pre-computed with the model
        self.cache={} # (form, upos, xpos, feats) -> lemma  
        self.read_cache(args.lemma_cache)
        self.lemmatize_url_and_email=args.lemmatize_url_and_email
        pass

    def read_cache(self, cache_file):
        """ make lemmatizer faster by keeping lemma cache (run lemmatizer only for words not in this cache) """
        with open(cache_file, "rt", encoding="utf8") as f:
            for line in f:
                form, upos, feats, lemma = line.strip().split("\t")
                self.cache[(form, upos, feats)]=lemma

    def is_url_or_email(self, word):
        if re.match(url_regex, word):
            return True
        if re.fullmatch(email_regex, word):
            return True
        return False

    def lemmatize_batch(self, conllu_batch):

        output_lines=[]
        lemmatized=0
        token_counter=0
        filled=0
        for (comm, sent) in read_conllu(conllu_batch.split("\n")):
            for c in comm:
                output_lines.append(c)
            for cols in sent:
                if "-" in cols[ID]: # multiword token line, not supposed to be analysed
                    output_lines.append("\t".join(t for t in cols))
                    continue
                token_counter+=1
                if cols[LEMMA]!="_": # already filled in for example by another module, do not process
                    cols[LEMMA]="_"
                #    output_lines.append("\t".join(t for t in cols))
                #    filled+=1
                #    continue
                token_data=(cols[FORM],cols[UPOS],cols[FEAT])
                if token_data in self.cache:
                    plemma=self.cache[token_data]
                    if plemma.strip()=="":
                        plemma="_" # make sure not to output empty lemma
                    cols[LEMMA]=plemma
                    output_lines.append("\t".join(t for t in cols))
                    lemmatized+=1
                    continue
                if self.lemmatize_url_and_email==False and self.is_url_or_email(cols[FORM]): # simple copy
                    cols[LEMMA]=cols[FORM]
                    output_lines.append("\t".join(t for t in cols))
                    lemmatized+=1
                    continue

                # lemma not in cache, pass empty lemma for next module
                output_lines.append("\t".join(t for t in cols))
            output_lines.append("")
        print(" >>> {}/{} lemmas already filled before lemma cache module".format(filled,token_counter),file=sys.stderr)
        print(" >>> {}/{} lemmatized with lemma cache".format(lemmatized,token_counter),file=sys.stderr)
        return "\n".join(output_lines)+"\n"

            
    def parse_text(self,conllu):
        result_conllu=self.lemmatize_batch(conllu)
        return result_conllu

    


def launch(args,q_in,q_out):
    lemma_cache=LemmaCacheWrapper(args)
    while True:
        jobid,txt=q_in.get()
        if jobid=="FINAL":
            q_out.put((jobid,txt))
            print("Lemma cache exiting",file=sys.stderr,flush=True)
            return
        q_out.put((jobid,lemma_cache.parse_text(txt)))

argparser = argparse.ArgumentParser(description='Lemmatize conllu text using precomputed lemma cache (comes together with the actual lemma model)')
argparser.add_argument('--lemma_cache', type=str, default='', help='Lemma cache file')
argparser.add_argument('--lemmatize_url_and_email', action="store_true", default=False, help='Lemmatize also URLs and emails (default: False -- copy form into lemma field)')
