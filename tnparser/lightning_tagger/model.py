

import torch
import argparse
import pytorch_lightning as pl
import torch.nn.functional as F
import transformers
import numpy
import logging
import torchmetrics

import torch
from torch.nn.parameter import Parameter
from pytorch_lightning.core.decorators import auto_move_data




class TaggerOutput(pl.LightningModule):

    def __init__(self, encoder_hidden_size, num_classes, dropout=0.3):
        super().__init__()
        self.dropout = torch.nn.Dropout(dropout)
        self.classifier = torch.nn.Linear(encoder_hidden_size, num_classes) # torch.nn.AdaptiveLogSoftmaxWithLoss 
                                                           
        

    def forward(self, encoder_hidden_states):
        
        #TODO: attention over hidden states
        
        encoder_hidden_states = self.dropout(encoder_hidden_states)
        logits = self.classifier(encoder_hidden_states)

        return logits



class TaggerModel(pl.LightningModule):

    def __init__(self, pretrained_bert = None, target_classes = {}, steps_train=None, weights=None):
        super().__init__()
        self.steps_train = steps_train
        self.target_classes = target_classes # key: name of the target layer, value: number of classes for the target
        self.weights = weights
        self.bert = transformers.BertModel.from_pretrained(pretrained_bert, output_hidden_states=True, return_dict=True)
        self.tokenizer = transformers.BertTokenizerFast.from_pretrained(pretrained_bert)
                                                           
        # layers for different label_sets (upos, feats ...)
        self.prediction_layers = torch.nn.ModuleDict()
        self.accuracies = torch.nn.ModuleDict()
        self.val_accuracies = torch.nn.ModuleDict()
        for target_name, num_classes in self.target_classes.items():
            logging.info(f"Creating prediction layer for '{target_name}' with {num_classes} classes")
            self.prediction_layers[target_name] = TaggerOutput(self.bert.config.hidden_size, num_classes)

            self.accuracies[target_name] = torchmetrics.Accuracy()
            self.val_accuracies[target_name] = torchmetrics.Accuracy()

    def forward(self, batch):
        outputs = self.bert(input_ids=batch['input_ids'],
                      attention_mask=batch['attention_mask'],
                      token_type_ids=batch['token_type_ids']) #BxS_LENxSIZE; BxSIZE
        
        last_hidden = outputs["last_hidden_state"]
        
        #TODO: attention over hidden states

        # run all prediction layers using encoder hiddens
        logits = {}
        for key in self.prediction_layers.keys():
            logits[key] = self.prediction_layers[key](last_hidden)

        return logits
        
        
        
    def freeze_encoder(self):
        for p in self.bert.embeddings.parameters():
            p.requires_grad = False
            
    def unfreeze_encoder(self):
        for p in self.bert.embeddings.parameters():
            p.requires_grad = True
        
        
    def training_step(self, batch, batch_idx):
        all_logits = self(batch)
        combined_loss = 0
        for key, logits in all_logits.items():
            loss = F.cross_entropy(logits.view(-1, self.target_classes[key]), batch["labels"][key].view(-1))
            combined_loss += loss
            logits = torch.nn.Softmax(dim=2)(logits)
            self.accuracies[key](logits.view(-1, self.target_classes[key]), batch["labels"][key].view(-1))
            self.log(f"train_acc_{key}", self.accuracies[key], prog_bar=False, on_step=True, on_epoch=True)
        self.log(f"combined_train_loss", combined_loss, prog_bar=False)
        return combined_loss

    def validation_step(self, batch, batch_idx):
        all_logits = self(batch)
        combined_loss = 0
        for key, logits in all_logits.items():
            loss = F.cross_entropy(logits.view(-1, self.target_classes[key]), batch["labels"][key].view(-1))
            combined_loss += loss
            logits = torch.nn.Softmax(dim=2)(logits)
            self.log(f"val_loss_{key}", loss, prog_bar=False)
            self.val_accuracies[key](logits.view(-1, self.target_classes[key]), batch["labels"][key].view(-1))
            self.log(f"val_acc_{key}", self.val_accuracies[key], prog_bar=True, on_epoch=True)
        self.log(f"val_loss", combined_loss, prog_bar=True)
        
    def test_step(self, batch, batch_idx):
        all_logits = self(batch)
        for key, logits in all_logits.items():
            logits = torch.nn.Softmax(dim=2)(logits)
            self.val_accuracies[key](logits.view(-1, self.target_classes[key]), batch["labels"][key].view(-1))
            self.log(f"test_acc_{key}", self.val_accuracies[key], prog_bar=True, on_epoch=True)
        
        
        
    @auto_move_data
    def predict(self, batch, batch_idx):
        all_logits = self(batch)
        output = {}
        for key, logits in all_logits.items():
            logits = torch.argmax(logits, dim=-1)
            output[key] = logits
        return output


    def configure_optimizers(self): # TODO
        optimizer = transformers.optimization.AdamW(self.parameters(), lr=0.0001)
        scheduler = transformers.optimization.get_linear_schedule_with_warmup(optimizer, num_warmup_steps=100, num_training_steps=7000)
        scheduler = {'scheduler': scheduler, 'interval': 'step', 'frequency': 1}
        return [optimizer], [scheduler]


