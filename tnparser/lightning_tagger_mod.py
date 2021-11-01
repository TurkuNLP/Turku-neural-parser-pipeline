import torch
import argparse
import pytorch_lightning as pl
import torch.nn.functional as F
import numpy
from tnparser.lightning_tagger.data import ConlluData, TaggerDataModule
from tnparser.lightning_tagger.model import TaggerModel
import os
import pickle
import logging
from tqdm import tqdm
import time
import sys
import traceback

logging.basicConfig(level=logging.INFO)


def load_model(args):
    logging.info(f"Loading model from {os.path.join(args.checkpoint_dir, 'best.ckpt')}")
    with open(os.path.join(args.checkpoint_dir, "label_encoders.pickle"), "rb") as f:
       label_encoders = pickle.load(f)
    target_classes = {}
    for label in label_encoders.keys():
        target_classes[label] = len(label_encoders[label].classes_)
    model = TaggerModel.load_from_checkpoint(pretrained_bert=args.bert_pretrained, target_classes=target_classes, checkpoint_path=os.path.join(args.checkpoint_dir, "best.ckpt"))
    model.freeze()
    model.eval()
    if torch.cuda.is_available():
        model.cuda()
    return model, label_encoders
    
    
def predict_batch(model, dataset, label_encoders):

    sent_counter = 0
    batch_labels = {}
    with torch.no_grad():
        for i, batch in enumerate(tqdm(dataset.test_dataloader())):
            predictions = model.predict(batch, i)
            subword_mask = batch["subword_mask"]
            for j, mask in enumerate(subword_mask): # iterate over sentences
                labels = {}
                for key, pred in predictions.items(): # iterate all label sets
                    pred = pred[j][mask != 0]
                    labels[key] = label_encoders[key].inverse_transform(pred.cpu())
                batch_labels[sent_counter] = labels
                sent_counter += 1
    logging.info(f"Predicted {sent_counter} sentences")
    return batch_labels


def launch(args, q_in, q_out):
    try:
        tagger, label_encoders = load_model(args)
        datareader = ConlluData()
    except:
        traceback.print_exc()
        sys.stderr.flush()
    while True:
        jobid,txt=q_in.get()
        if jobid=="FINAL":
            q_out.put((jobid,txt))
            return
        try:
            # prepare dataset
            sentences = []
            for comm, sent in datareader.read_conllu(txt):
                sentences.append((comm, sent))
            data = datareader.data2dict(sentences)
            dataset = TaggerDataModule(tagger.tokenizer, label_encoders, args.batch_size)
            dataset.prepare_data(data, stage="predict")
            dataset.setup("predict")
            
            # predict
            batch_labels = predict_batch(tagger, dataset, label_encoders)
            pred = []
            for sent_idx, labels in batch_labels.items():
                conllu = datareader.write_predictions(data, labels, sent_idx)
                pred += conllu
            q_out.put((jobid,"\n".join(pred)))
        except:
            traceback.print_exc()
            sys.stderr.flush()
            raise
    

argparser = argparse.ArgumentParser()
argparser.add_argument('--bert_pretrained', type=str, default='TurkuNLP/bert-base-finnish-cased-v1')
argparser.add_argument('--batch_size', type=int, default=16)
argparser.add_argument('--checkpoint_dir', default="checkpoints", type=str)

