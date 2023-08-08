import json
from api_utils import query_chatgpt
from apikeys import APIKEYS, GPT4_APIKEYS
import argparse
from utils import Classifier
import os
from data_filter import DataFilter
from prompt import general_filter_template5

def read_gpt4_response(input_path):
    prompts = []
    labels = []

    with open(input_path) as f:
        for i,l in enumerate(f):
            example=json.loads(l.strip())
            try:
                prompt=example['gpt4_request']['messages'][0]['content']
                label=example['gpt4_response']['choices'][0]['message']['content']
            except Exception:
                print(example['gpt4_response'])
                continue
            if label.lower() not in ('yes', 'no'):
                continue
            if label.lower() == 'yes':
                labels.append(1)
            else:
                labels.append(-1)

            prompts.append(prompt)

def read_human_data(input_path):
    prompts = []
    labels = []

    with open(input_path) as f:
        for i,l in enumerate(f):
            example=json.loads(l.strip())
            try:
                prompt=example['content']
                label=example['final_result'].lower()
            except Exception:
                print(example)
                continue
            
            if label not in ('yes', 'no'):
                continue

            if label == 'yes':
                label = 1
            else:
                label = -1
            labels.append(label)
            prompts.append(prompt)
    return prompts, labels

def classify_based_on_gpt(
        texts, labels, gpt_model, template, gpt_outputs_path=None, 
        do_fit=False, do_cross_validation=False, do_test=False, classifier_path=None):
    data_filter = DataFilter.build_filter(template)

    print('data size:',len(texts))

    gpt_outputs = data_filter.query(
        texts=texts,
        engine=gpt_model, 
        gpt_outputs_path=gpt_outputs_path,
        num_processes=10, 
        retry_limit=5,
        temperature=0.)
    
    print(f"current get {len(gpt_outputs)} gpt output, total {len(texts)}")

    gpt_outputs_preds = []
    gpt_outputs_labels = []
    for d in gpt_outputs:
        d['text'] = texts[d['id']]
        d['label'] = labels[d['id']]
        gpt_outputs_preds.append(d['output'])
        gpt_outputs_labels.append(labels[d['id']])
        
    if do_cross_validation or do_fit or do_test:
        assert len(gpt_outputs_preds[0])>1 # multiple features dimensions

    if do_fit:
        classifier = Classifier()
        classifier.fit(gpt_outputs_preds, gpt_outputs_labels)
        classifier.save_model(classifier_path)
    if do_cross_validation:
        classifier = Classifier()
        classifier.cross_validate(gpt_outputs_preds,gpt_outputs_labels)
    if do_test:
        classifier = Classifier()
        classifier.load_model(classifier_path)
        print(classifier.test(gpt_outputs_preds, gpt_outputs_labels))



if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Description of your script')
    parser.add_argument('--input_path', help='Help message for arg_name')
    parser.add_argument('--output_dir', help='Help message for arg_name')
    parser.add_argument('--output_name', help='Help message for arg_name')
    parser.add_argument('--do_fit', action='store_true', help='Help message for arg_name')
    parser.add_argument('--do_test', action='store_true', help='Help message for arg_name')
    parser.add_argument('--do_cross_validation', action='store_true', help='Help message for arg_name')

    args = parser.parse_args()

    gpt3_model = 'gpt-3.5-turbo'
    gpt4_model = 'gpt-4'
    output_dir = args.output_dir
    output_name = args.output_name
    # texts 是文本， labels是标签， 正常样本 1， 脏样本 -1
    texts, labels = read_human_data(args.input_path)


    # import pdb
    # pdb.set_trace()
    classify_based_on_gpt(
        texts, labels,
        gpt_model=gpt3_model, 
        template=general_filter_template5, 
        gpt_outputs_path=f'${output_dir}//${output_name}_gptoutputs_template5_{gpt3_model}.jsonl', 
        do_fit=args.do_fit,
        do_cross_validation=args.do_cross_validation,
        do_test=args.do_test,
        classifier_path=f'${output_dir}//classifier_template5_{gpt3_model}.joblib')