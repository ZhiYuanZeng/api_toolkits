from ad_filter import AdFilter, template1
import argparse
import json
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score

def eval_template(template, texts, labels, output_path):
    data_filter = AdFilter.build_filter(template)
    gpt_outputs = data_filter.query(
        texts=texts,
        engine='gpt-3.5-turbo', 
        gpt_outputs_path=output_path,
        num_processes=10, 
        retry_limit=5,
        temperature=0.)

    scores = [0 for _ in range(len(labels))]
    preds = [0 for _ in range(len(labels))]
    

    for o in gpt_outputs:
        if o is not None:
            score = int(o['output'])
            id = int(o['id'])
            scores[id] = score
            # score < 5 认为是正样本， score越高，说明越是广告
            preds[id] = (score<5)
    
    fo = None
    print(f'using templat:.................................', file=fo)
    print(template)

    import pdb
    pdb.set_trace()

    print('acc:', accuracy_score(labels, preds), file=fo)
    print('f1:', f1_score(labels, preds), file=fo)
    print('precision_score:', precision_score(labels, preds), file=fo)
    print('recall_score:', recall_score(labels, preds), file=fo)
    print('--------------------------------------\n\n', file=fo)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Description of your script')
    parser.add_argument('--input_path', help='Help message for arg_name')
    parser.add_argument('--output_path', help='Help message for arg_name')
    args = parser.parse_args()
    output_path = args.output_path
    texts = []
    labels = []
    with open(args.input_path, 'r') as f:
        for l in f:
            try:
                data = json.loads(l)
            except Exception as e:
                print(l)
                raise e
            texts.append(data['content'])
            if data['final_result'] == "no":
                labels.append(0)
            else:
                labels.append(1)
    import pdb
    pdb.set_trace()
    
    eval_template(template1, texts, labels, output_path)
 

