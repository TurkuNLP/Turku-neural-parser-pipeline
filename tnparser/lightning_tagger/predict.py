import torch
import argparse
import pytorch_lightning as pl
import torch.nn.functional as F
import transformers
import numpy
from sklearn.preprocessing import LabelEncoder
from tnparser.lightning_tagger.data import TaggerDataModule, ConlluData
from tnparser.lightning_tagger.model import TaggerModel
import os
import sys
import pickle
import logging
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)

def main(args):

    # read data
    datareader = ConlluData()
    with open(args.data, "rt", encoding="utf-8") as f:
        data = [s for s in datareader.read_conllu(f)]
    data = datareader.data2dict(data)

    # load model
    if not os.path.exists(args.checkpoint_dir):
        logging.error(f"Checkpoint directory {args.checkpoint_dir} does not exists!")
        sys.exit()
    logging.info(f"Loading model from {os.path.join(args.checkpoint_dir, 'best.ckpt')}")
    with open(os.path.join(args.checkpoint_dir, "label_encoders.pickle"), "rb") as f:
       label_encoders = pickle.load(f)
    target_classes = {}
    for label in label_encoders.keys():
        target_classes[label] = len(label_encoders[label].classes_)
    model = TaggerModel.load_from_checkpoint(pretrained_bert=args.bert_pretrained, target_classes=target_classes, checkpoint_path=os.path.join(args.checkpoint_dir, "best.ckpt"))
    model.eval()
        

    # create dataset
    logging.info("Creating a dataset")
    dataset = TaggerDataModule(model.tokenizer, label_encoders, args.batch_size)
    dataset.prepare_data(data, stage="predict")
    dataset.setup("predict")

    
    # predict
    if torch.cuda.is_available():
        model.cuda()
        
    sent_counter = 0
    
    conllus = []
    with torch.no_grad():
        for i, batch in enumerate(tqdm(dataset.test_dataloader())):
            predictions = model.predict(batch, i)
            subword_mask = batch["subword_mask"]
            for i, mask in enumerate(subword_mask): # iterate over sentences
                labels = {}
                for key, pred in predictions.items(): # iterate all label sets
                    pred = pred[i][mask != 0]
                    labels[key] = label_encoders[key].inverse_transform(pred.cpu())
                conllu = datareader.write_predictions(data, labels, sent_counter)
                conllus += conllu
                sent_counter += 1
    
    
    logging.info("Prediction done!")

    print("\n".join(conllus))
    
    

    
    






          
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='data/dev.conllu')
    parser.add_argument('--bert_pretrained', type=str, default='TurkuNLP/bert-base-finnish-cased-v1')
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--checkpoint_dir', default="checkpoints", type=str)
    
    args = parser.parse_args()
    
    main(args)
