import json
import argparse
from data_rewrite import DataRewritter
from data_filter import template5
from run_data_filter import read_human_data, classify_based_on_gpt

def read_rewrited_data(input_path):
    prompts = []
    labels = []

    with open(input_path) as f:
        for i,l in enumerate(f):
            example=json.loads(l.strip())
            try:
                prompt=example['output']['text']
                label=example['output']['label']
            except Exception as e:
                print('reading rewritted data error, here is the data:', example)
                raise e
            
            if label != 1:
                continue

            labels.append(label)
            prompts.append(prompt)
    return prompts, labels

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Description of your script')
    parser.add_argument('--gpt_feature_path', help='Help message for arg_name')
    parser.add_argument('--text_path', help='Help message for arg_name')
    parser.add_argument('--refined_text_path', help='Help message for arg_name')
    parser.add_argument('--do_refine', action='store_true', help='Help message for arg_name')
    parser.add_argument('--do_test', action='store_true', help='Help message for arg_name')

    args = parser.parse_args()

    if args.do_refine:
        texts, labels = read_human_data(args.text_path)
        texts_to_rewrite = []
        with open(args.gpt_feature_path, 'r') as f:
            for l in f:
                d = json.loads(l)
                label = labels[d['id']]
                safety_score = d['output'][0]
                text = texts[d['id']]
                if safety_score > 0 and label == -1:
                    texts_to_rewrite.append(text)

        rewritter = DataRewritter.build_filter()

        print(f'original data size:{len(texts)}, data to be rewrited size:{len(texts_to_rewrite)}')
        gpt_outputs = rewritter.query(
                texts=texts_to_rewrite,
                engine='gpt-3.5-turbo',
                gpt_outputs_path=args.refined_text_path,
                num_processes=10, 
                retry_limit=5,
                temperature=0.)
    
    elif args.do_test:
        texts, labels = read_rewrited_data(args.refined_text_path)
        gpt3_model = 'gpt-3.5-turbo'
        classify_based_on_gpt(
            texts, labels,
            gpt_model=gpt3_model, 
            template=template5, 
            gpt_outputs_path=None, 
            do_fit=False,
            do_cross_validation=False,
            do_test=True,
            classifier_path=f'./classifier_template5_{gpt3_model}.joblib')
