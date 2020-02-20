from tnparser.pipeline import Pipeline, read_pipelines
import sys
import select
import os
import yaml
import time
import gzip
import re


def batch_endswith_text(lines):
    global comment_regex
    for line in lines[::-1]:
        if not line.strip(): #skip empty lines
            continue
        if comment_regex.match(line):
            return False
        return True
    return False

def batch_has_text(lines):
    global comment_regex
    for line in lines:
        if not line.strip():
            continue
        if comment_regex.match(line):
            continue
        return True
    return False
    

if __name__=="__main__":
    import argparse
    THISDIR=os.path.dirname(os.path.abspath(__file__))

    argparser = argparse.ArgumentParser(description='Parser pipeline')
    general_group = argparser.add_argument_group(title='General', description='General pipeline arguments')
    general_group.add_argument('--conf-yaml', default=os.path.join(THISDIR,"pipelines.yaml"), help='YAML with pipeline configs. Default: parser_dir/pipelines.yaml')
    general_group.add_argument('--pipeline', default="parse_plaintext", help='[DEPRECATED] Name of the pipeline to run, one of those given in the YAML file. Default: %(default)s')
    general_group.add_argument('--empty-line-batching', default=False, action="store_true", help='Only ever batch on newlines (useful with pipelines that input conllu)')
    general_group.add_argument('--batch-lines', default=1000, type=int, help='Number of lines in a job batch. Default %(default)d, consider setting a higher value if using conllu input instead of raw text (maybe 5000 lines), and try smaller values in case of running out of memory with raw text.')
    general_group.add_argument('action', default=None, nargs='?', help="What to do. Either 'list' to lists pipelines or a pipeline name to parse, or nothing in which case the default parse_plaintext is used.")

    lemmatizer_group = argparser.add_argument_group(title='lemmatizer_mod', description='Lemmatizer arguments')
    lemmatizer_group.add_argument('--gpu', dest='lemmatizer_mod.gpu', type=int, default=0, help='GPU device id for the lemmatizer, if -1 use CPU')
    lemmatizer_group.add_argument('--batch_size', dest='lemmatizer_mod.batch_size', type=int, default=100, help='Lemmatizer batch size')


    args = argparser.parse_args()


    pipelines=read_pipelines(args.conf_yaml)

    if args.action=="list":
        print(sorted(pipelines.keys()),file=sys.stderr,flush=True)
        sys.exit(0)
    elif args.action is not None and args.action!="parse": #deprecated legacy stuff, allowing calls like --pipeline pipelinename parse
        pipeline=pipelines[args.action]
    elif args.action is None or args.action=="parse":
        pipeline=pipelines[args.pipeline]
        
    if pipeline[0].startswith("extraoptions"):
        extraoptions=pipeline[0].split()[1:]
        pipeline.pop(0)
        newoptions=extraoptions+sys.argv[1:]
        print("Got extra arguments from the pipeline, now running with", newoptions, file=sys.stderr, flush=True)
        args=argparser.parse_args(newoptions)

    pipeline.append("output_mod")
    p=Pipeline(steps=pipeline, extra_args=args)

    print("Waiting for input",file=sys.stderr,flush=True)
    comment_regex=re.compile("^####?C:")
    line_buffer=[]
    for line in sys.stdin:
        line_buffer.append(line)
        if not comment_regex.match(line) and (line.strip()=="" or not args.empty_line_batching) and len(line_buffer)>args.batch_lines and batch_endswith_text(line_buffer):
            if not p.is_alive(): #gotta end if something dies
                print("Something crashed. Exiting.",file=sys.stderr,flush=True)
                sys.exit(-1)
            print("Feeding a batch",file=sys.stderr,flush=True)
            p.put("".join(line_buffer))
            line_buffer=[]
    else:
        if line_buffer:
            if not batch_has_text(line_buffer):
                print("WARNING: Comments and empty lines at the end of the input will be removed in order to produce valid conll-u. The input must not end with comments",file=sys.stderr,flush=True)
            else:
                if not p.is_alive(): #gotta end if something dies
                    print("Something crashed. Exiting.",file=sys.stderr,flush=True)
                    sys.exit(-1)
                print("Feeding final batch",file=sys.stderr,flush=True)
                p.put("".join(line_buffer))

    p.send_final()
    p.join()

