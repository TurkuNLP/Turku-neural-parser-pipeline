import torch
import argparse
import pytorch_lightning as pl
import torch.nn.functional as F
import transformers
import numpy
from sklearn.preprocessing import LabelEncoder
from tnparser.lightning_tagger.data import ConlluData, TaggerDataModule
from tnparser.lightning_tagger.model import TaggerModel
#from callbacks import FinetuneFreezer
import os
import pickle
import logging




logging.basicConfig(level=logging.INFO)

def all_labels(data):
    all_labels = set()
    for example in data:
        for key in example["labels"].keys():
            all_labels.add(key)
    logging.info("LABEL SETS: " + ", ".join(list(all_labels)))
    return all_labels


def fit_label_encoders(data, label_sets):
    
    label_encoders = {}
    for label in label_sets: # TODO fix here
        label_encoder = LabelEncoder()
        label_encoder.fit([l for e in data for l in e["labels"][label]])
        logging.info(f"Label encoder: {label}, labels: {label_encoder.classes_}")
        label_encoders[label] = label_encoder
    return label_encoders



def main(args):

    # read data
    logging.info("Reading data")
    datareader = ConlluData()
    with open(args.train_data, "rt", encoding="utf-8") as f:
        train_data = [s for s in datareader.read_conllu(f)]
    with open(args.eval_data, "rt", encoding="utf-8") as f:
        eval_data = [s for s in datareader.read_conllu(f)]

    train_data = datareader.data2dict(train_data)
    eval_data = datareader.data2dict(eval_data)

    label_sets = all_labels(train_data+eval_data)

    # model checkpoint not available
    if not os.path.exists(args.checkpoint_dir):
        logging.info(f"Creating directory {args.checkpoint_dir}")
        os.makedirs(args.checkpoint_dir)
        
    # create label encoder and model
    logging.info(f"Fitting label encoder")
    label_encoders = fit_label_encoders(train_data+eval_data, label_sets)
    target_classes = {}
    for label in label_sets:
        target_classes[label] = len(label_encoders[label].classes_)
      
    logging.info(f"Saving label encoder into {os.path.join(args.checkpoint_dir, 'label_encoder.pickle')}")
    with open(os.path.join(args.checkpoint_dir, "label_encoders.pickle"), "wb") as f:
        pickle.dump(label_encoders, f)
        
    logging.info(f"Creating model")
    # initialize tagger model
    model = TaggerModel(target_classes, pretrained_bert=args.pretrained_bert)
    model.load_pretrained() # load pretrained bert weigths
        
        
#    else:
#        logging.info(f"Loading model from {os.path.join(args.checkpoint_dir, 'best.ckpt')}")
#        with open(os.path.join(args.checkpoint_dir, "label_encoders.pickle"), "rb") as f:
#           label_encoders = pickle.load(f)
#        model = TaggerModel.load_from_checkpoint(os.path.join(args.checkpoint_dir, "best.ckpt"))
        

    # create dataset
    
    logging.info("Creating a dataset")
    dataset = TaggerDataModule(model.tokenizer, label_encoders, args.batch_size)
    dataset.prepare_data((train_data, eval_data), stage="fit")
    dataset.setup("fit")
    
    size_train = len(dataset.train_data)
    steps_per_epoch = int(size_train/args.batch_size)
    steps_train = steps_per_epoch*args.epochs
    
    # callbacks
    checkpoint_callback = pl.callbacks.ModelCheckpoint(monitor='val_loss', dirpath=args.checkpoint_dir, filename='best', save_top_k=1, mode='min', save_last=True, save_weights_only=True, verbose=True)
    #freezer_callback = FinetuneFreezer(unfreeze_epoch=args.freeze_encoder)
    
    # train
    gpu=0
    if torch.cuda.is_available():
        model.cuda()
        gpu=1
    #trainer = pl.Trainer(gpus=1, callbacks=[checkpoint_callback, freezer_callback], max_epochs=args.epochs)
    trainer = pl.Trainer(gpus=gpu, callbacks=[checkpoint_callback], max_epochs=args.epochs)
    trainer.fit(model, dataset.train_dataloader(), dataset.val_dataloader())
    logging.info("Training done!")
    
    # test
    logging.info("Evaluating on development data")
    trainer.test(model, dataset.val_dataloader())
    


          
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--train_data', type=str, default='data/train.conllu')
    parser.add_argument('--eval_data', type=str, default='data/dev.conllu')
    parser.add_argument('--pretrained_bert', type=str, default='TurkuNLP/bert-base-finnish-cased-v1')
    parser.add_argument('--batch_size', type=int, default=14)
    parser.add_argument('--epochs', type=int, default=8)
    parser.add_argument('--freeze_encoder', type=int, default=0, help="Freeze bert encoder weights for x epochs. (Default is 0, no freezing)")
    parser.add_argument('--checkpoint_dir', default="checkpoints", type=str)
    parser.add_argument('--datareader', default="conllu", type=str) # TODO options
    
    args = parser.parse_args()
    
    main(args)
