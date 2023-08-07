from knowledge_filter import KnowledgeFilter, template1, template2, template3
import argparse
import json
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score

def eval_template(template, texts, labels):
    data_filter = KnowledgeFilter.build_filter(template)
    gpt_outputs = data_filter.query(
        texts=texts,
        engine='gpt-3.5-turbo', 
        gpt_outputs_path=None,
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
            preds[id] = (score>=5)

    categories = ['wiki', 'paper', 'news', 'twitter', 'moviw review', 'book']
    fo = None
    print(f'using templat:.................................', file=fo)
    print(template)

    for i in range(len(preds)//10):
        print(categories[i],'..........................', file=fo)
        s,e = 10*i, 10*(i+1)
        print(labels[s:e], file=fo)
        print(scores[s:e], file=fo)
        print('acc:', accuracy_score(labels[s:e], preds[s:e]), file=fo)
        print('f1:', f1_score(labels[s:e], preds[s:e]), file=fo)
        print('precision_score:', precision_score(labels[s:e], preds[s:e]), file=fo)
        print('recall_score:', recall_score(labels[s:e], preds[s:e]), file=fo)
    print('--------------------------------------\n\n', file=fo)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Description of your script')
    parser.add_argument('--input_path', help='Help message for arg_name')
    args = parser.parse_args()

    texts = []
    labels = []
    with open(args.input_path, 'r') as f:
        for l in f:
            try:
                d = json.loads(l)
            except Exception as e:
                print(l)
                raise e
            texts.append(d['text'])
            labels.append(d['label'])
    eval_template(template2, texts, labels)
 

