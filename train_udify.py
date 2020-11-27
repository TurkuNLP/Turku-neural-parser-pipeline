
import os
import copy
import datetime
import logging
import argparse
import glob

from allennlp.common import Params
from allennlp.common.util import import_submodules
from allennlp.commands.train import train_model

from tnparser import udify
import tnparser.udify.util

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("--name", required=True, type=str, help="Log dir name")
parser.add_argument("--config", required=True, type=str, help="Configuration file")
parser.add_argument("--config-base", default="templates/udify_base.json", type=str, help="Base configuration file")
parser.add_argument("--config-vocab", default="templates/udify_vocab.json", type=str, help="Vocab configuration file")
parser.add_argument("--data-dir", required=True, type=str, help="The path containing UD treebanks files for training")
parser.add_argument("--batch_size", default=32, type=int, help="The batch size used by the model; the number of training sentences is divided by this number.")
parser.add_argument("--device", default=None, type=int, help="CUDA device; set to -1 for CPU")
parser.add_argument("--resume", type=str, help="Resume training with the given model")
parser.add_argument("--lazy", default=None, action="store_true", help="Lazy load the dataset")
parser.add_argument("--cleanup_archive", action="store_true", help="Delete the model archive")
parser.add_argument("--replace_vocab", action="store_true", help="Create a new vocab and replace the cached one")
parser.add_argument("--archive_bert", action="store_true", help="Archives the finetuned BERT model after training")
parser.add_argument("--predictor", default="udify_predictor", type=str, help="The type of predictor to use")

args = parser.parse_args()

log_dir_name = args.name

train_file = args.name + "-ud-train.conllu"
logger.info(f"train_file: {train_file}")
train_path = os.path.join(args.data_dir, train_file)
logger.info(f"train_path: {train_path}")

if train_path:
    logger.info(f"found training file: {train_path}, calculating the warmup and start steps")

    with open(train_path, 'r', encoding="utf-8") as f:
        sentence_count = 0
        for line in f.readlines():
            if line.isspace():
                sentence_count += 1
    num_warmup_steps = round(sentence_count / args.batch_size)
    logger.info(f"num_warmup_steps: {num_warmup_steps}")

configs = []

if not args.resume:
    
    serialization_dir = os.path.join("logs", log_dir_name)
    model_dir = os.path.join("logs", log_dir_name, "model")

    overrides = {}
    if args.device is not None:
        overrides["trainer"] = {"cuda_device": args.device}
    if args.lazy is not None:
        overrides["dataset_reader"] = {"lazy": args.lazy}
    configs.append(Params(overrides))
    configs.append(Params.from_file(args.config))
    configs.append(Params.from_file(args.config_base))
else:
    serialization_dir = args.resume
    configs.append(Params.from_file(os.path.join(serialization_dir, "config.json")))

train_params = tnparser.udify.util.merge_configs(configs)
for param in train_params:
    print(param)


for param in train_params:
    if param == "train_data_path":
        train_params["train_data_path"] = train_path
    if param == "validation_data_path":
        train_params["validation_data_path"] = os.path.join(args.data_dir, f"{args.name}-ud-dev.conllu")
    
    if param == "vocabulary":
        train_params["vocabulary"]["directory_path"] = f"{serialization_dir}/vocabulary"
    
    if param == "trainer":
        for sub_param in train_params["trainer"]:
            if sub_param == "learning_rate_scheduler":
                train_params["trainer"]["learning_rate_scheduler"]["warmup_steps"] = num_warmup_steps
                train_params["trainer"]["learning_rate_scheduler"]["start_step"] = num_warmup_steps
                
                logger.info(f"changing warmup and start steps for {train_path} to {num_warmup_steps}")
                
if "vocabulary" in train_params:
    # Remove this key to make AllenNLP happy
    train_params["vocabulary"].pop("non_padded_namespaces", None)

predict_params = train_params.duplicate()

import_submodules("tnparser.udify")


# train
try:
    tnparser.udify.util.cache_vocab(train_params, args.config_vocab)
    train_model(train_params, model_dir, recover=bool(args.resume))
except KeyboardInterrupt:
    logger.warning("KeyboardInterrupt, skipping training")

dev_file = predict_params["validation_data_path"]
#test_file = predict_params["test_data_path"]

#dev_pred, dev_eval, test_pred, test_eval = [
#    os.path.join(serialization_dir, name)
#    for name in ["dev.conllu", "dev_results.json", "test.conllu", "test_results.json"]
#]

dev_pred, dev_eval = [os.path.join(model_dir, name) for name in ["dev.conllu", "dev_results.json"]]

# predict on development file
tnprser.udify.util.predict_and_evaluate_model(args.predictor, predict_params, model_dir, dev_file, dev_pred, dev_eval)

#util.predict_and_evaluate_model(args.predictor, predict_params, serialization_dir, test_file, test_pred, test_eval)

#if args.archive_bert:
#    bert_config = "config/archive/bert-base-multilingual-cased/bert_config.json"
#    util.archive_bert_model(serialization_dir, bert_config)

# TODO
tnparser.udify.util.cleanup_training(model_dir, keep_archive=not args.cleanup_archive)

