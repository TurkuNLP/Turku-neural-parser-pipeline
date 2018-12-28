# Usage: cat big_parsed_file.conllu | python build_lemma_cache.py > lemma_cache.tsv

import sys
import unicodedata

ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC = range(10)


def build(args):
    words={}

    for line in sys.stdin:
        line=line.strip()
        if not line or line.startswith("#"):
            continue
        cols=line.split("\t")
        word=(cols[FORM], cols[UPOS], cols[XPOS], cols[FEATS], cols[LEMMA])
        if word not in words:
            words[word]=0
        words[word]+=1

    for word, count in sorted(words.items(), key=lambda x: x[1], reverse=True):

        if count>args.cutoff:
            w="\t".join(word)
            if len(w.strip().split("\t"))!=5: # make sure there is no empty columns
                print("Skipping weird line", w, file=sys.stderr)
                continue
            print(w)
        else:
            break


if __name__=="__main__":
    import argparse
    argparser = argparse.ArgumentParser(description='Build lemma cache')
    argparser.add_argument('--cutoff', default=5, type=int, help='Minimum word frequency for words to be included in the lemma cache')

    args = argparser.parse_args()

    build(args)
