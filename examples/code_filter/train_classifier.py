import torch
import json
from transformers import (
    AutoTokenizer,
    AutoConfig,
    AutoModel,
    Trainer,
    TrainingArguments,
    CodeGenPreTrainedModel,
    CodeGenModel,
    DataCollatorWithPadding,
    TrainerCallback,
)
from transformers.modeling_outputs import SequenceClassifierOutputWithPast
from torch import nn
from torch.nn import CrossEntropyLoss, MSELoss, BCEWithLogitsLoss
from typing import Optional, Tuple, Union
import torch
import torch.nn as nn
from datasets import load_dataset
from datasets import load_metric
import numpy as np
from tqdm import tqdm

class GodeGenForSequenceClassification(CodeGenPreTrainedModel):
    _keys_to_ignore_on_load_missing = [r"h\.\d+\.attn\.masked_bias", r"lm_head.weight"]

    def __init__(self, config):
        super().__init__(config)
        self.num_labels = config.num_labels
        self.transformer = CodeGenModel(config)
        self.score = nn.Linear(config.n_embd, self.num_labels, bias=False)

        # Model parallel
        self.model_parallel = False
        self.device_map = None

        # Initialize weights and apply final processing
        self.post_init()

    def forward(
        self,
        input_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[Tuple[Tuple[torch.Tensor]]] = None,
        attention_mask: Optional[torch.FloatTensor] = None,
        token_type_ids: Optional[torch.LongTensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        head_mask: Optional[torch.FloatTensor] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        labels: Optional[torch.LongTensor] = None,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
    ) -> Union[Tuple, SequenceClassifierOutputWithPast]:
        r"""
        labels (`torch.LongTensor` of shape `(batch_size,)`, *optional*):
            Labels for computing the sequence classification/regression loss. Indices should be in `[0, ...,
            config.num_labels - 1]`. If `config.num_labels == 1` a regression loss is computed (Mean-Square loss), If
            `config.num_labels > 1` a classification loss is computed (Cross-Entropy).
        """
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        # print(input_ids)
        # print(attention_mask)
        # print(position_ids)
        transformer_outputs = self.transformer(
            input_ids,
            past_key_values=past_key_values,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )
        hidden_states = transformer_outputs[0]
        logits = self.score(hidden_states)

        if input_ids is not None:
            batch_size, sequence_length = input_ids.shape[:2]
        else:
            batch_size, sequence_length = inputs_embeds.shape[:2]

        assert (
            self.config.pad_token_id is not None or batch_size == 1
        ), "Cannot handle batch sizes > 1 if no padding token is defined."
        if self.config.pad_token_id is None:
            sequence_lengths = -1
        else:
            if input_ids is not None:
                sequence_lengths = (torch.ne(input_ids, self.config.pad_token_id).sum(-1) - 1).to(logits.device)
            else:
                sequence_lengths = -1
                print(
                    f"{self.__class__.__name__} will not detect padding tokens in `inputs_embeds`. Results may be "
                    "unexpected if using padding tokens in conjunction with `inputs_embeds.`"
                )

        pooled_logits = logits[torch.arange(batch_size, device=logits.device), sequence_lengths]

        loss = None
        if labels is not None:
            if self.config.problem_type is None:
                if self.num_labels == 1:
                    self.config.problem_type = "regression"
                elif self.num_labels > 1 and (labels.dtype == torch.long or labels.dtype == torch.int):
                    self.config.problem_type = "single_label_classification"
                else:
                    self.config.problem_type = "multi_label_classification"

            if self.config.problem_type == "regression":
                loss_fct = MSELoss()
                if self.num_labels == 1:
                    loss = loss_fct(pooled_logits.squeeze(), labels.squeeze())
                else:
                    loss = loss_fct(pooled_logits, labels)
            elif self.config.problem_type == "single_label_classification":
                loss_fct = CrossEntropyLoss()
                loss = loss_fct(pooled_logits.view(-1, self.num_labels), labels.view(-1))
            elif self.config.problem_type == "multi_label_classification":
                loss_fct = BCEWithLogitsLoss()
                loss = loss_fct(pooled_logits, labels)
        if not return_dict:
            output = (pooled_logits,) + transformer_outputs[1:]
            return ((loss,) + output) if loss is not None else output

        return SequenceClassifierOutputWithPast(
            loss=loss,
            logits=pooled_logits,
            past_key_values=transformer_outputs.past_key_values,
            hidden_states=transformer_outputs.hidden_states,
            attentions=transformer_outputs.attentions,
        )

class CustomCallback(TrainerCallback):
    
    def __init__(self, model, eval_dataset) -> None:
        super().__init__()
        self.model = model
        self.eval_dataset =eval_dataset
    
    def on_save(self, args, state, control, **kwargs):
        evaluate(self.model, self.eval_dataset)
            
# Set up configuration
# model_name = "Salesforce/codegen2-1B"
model_name = "/mnt/petrelfs/zengzhiyuan.d/code_distill/results/checkpoint-25000"
max_length=1024
tokenizer = AutoTokenizer.from_pretrained(model_name)
config = AutoConfig.from_pretrained(model_name, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

# Set up data
# raw_datasets = load_dataset("glue", "mrpc")
raw_datasets = load_dataset('json', data_files={
    'train':['./datasets.train.json'], 
    'validation':['./datasets.valid.json'], 
    'test':['./datasets.test.json']})

# Tokenize data
def tokenize_func(example):
    tokenized_example = tokenizer(example['text'], max_length = max_length, truncation=True, padding='max_length')
    assert len(tokenized_example['input_ids'])<=max_length
    return tokenized_example

tokenized_datasets = raw_datasets.map(tokenize_func)
model = GodeGenForSequenceClassification.from_pretrained(model_name)
model.config.pad_token_id = tokenizer.eos_token_id
device=torch.device('cuda')
model.to(device)

# Set up training arguments
training_args = TrainingArguments(
    num_train_epochs=3,
    per_device_train_batch_size=8,
    learning_rate=1e-5,
    fp16=True,
    logging_strategy='steps',
    logging_steps=100,
    output_dir='results/',
    save_strategy='steps',
    save_steps=5000
)
# Set up the Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets['train'],
    tokenizer=tokenizer,
)
trainer.add_callback(CustomCallback(model, tokenized_datasets['validation']))

def evaluate(model, eval_dataset):
    avg_acc = []
    precision = []
    recall =[]
    print('do eval.......................')
    for d in tqdm(eval_dataset):
        input_ids = torch.LongTensor(d['input_ids']).unsqueeze(dim=0).to(device)
        attention_mask = torch.LongTensor(d['attention_mask']).unsqueeze(dim=0).to(device)
        outputs = model(input_ids = input_ids, attention_mask = attention_mask, return_dict=True)
        logits = outputs['logits']
        prediction = logits[0,0].item() < logits[0,1].item()
        label = int(d['label'])
        avg_acc.append(prediction==label)
        if prediction == 1:
            precision.append(prediction==label)
        if label==1:
            recall.append(prediction==label)
    avg_acc = sum(avg_acc)/len(avg_acc)
    precision = sum(precision)/len(precision)
    recall = sum(recall)/len(recall)
    print(f'{avg_acc=}, {precision=}, {recall=}, ')

evaluate(model, tokenized_datasets['test'])
# trainer.train()