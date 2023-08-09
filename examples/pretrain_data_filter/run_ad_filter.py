from ad_filter import AdFilter
from prompt import ad_filter_template1, ad_filter_template2, ad_filter_template3
import io
import csv
import argparse
import json
from utils import create_output_path
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score
from sklearn.metrics import precision_recall_curve
import os
from sklearn.metrics import confusion_matrix
def eval_template(template, texts, labels, output_path, eval_report=False):
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
    

    fo = None
    print(f'using templat:.................................', file=fo)
    print(template)
    eval_result = ["id,text,label,preds,score"]
    threshes = [ i for i in range(1,10)]
    print(f"output path:{output_path}")
    for thresh in threshes:
        for o in gpt_outputs:
            if o is not None:
                score = int(o['score'])
                id = int(o['id'])
                scores[id] = score
                # 为了计算广告的precison, recall,
                # score >= 5 认为是1，为广告 score越高，说明越是广告。 score低为无广告
                preds[id] = (score>=thresh)
        
        print(f"thresh: {thresh}")
        print('acc:', accuracy_score(labels, preds), file=fo)
        print('f1:', f1_score(labels, preds), file=fo)
        print('precision_score:', precision_score(labels, preds), file=fo)
        print('recall_score:', recall_score(labels, preds), file=fo)

        # 确认混淆矩阵输出所有类
        tn, fp, fn, tp = confusion_matrix(labels, preds).ravel()
    
        print(f'confuse_matrix: (tn:{tn}, fp:{fp}, fn:{fn}, tp:{tp})',)

        print('--------------------------------------\n', file=fo)

        if eval_report:
            report_name = os.path.join(os.path.dirname(output_path), os.path.basename(output_path).split(".")[0] + f"_thresh{thresh}_report.csv")

            with io.open(report_name, 'w', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["id", "text", "label", "preds", "score"])
                for i in range(len(labels)):
                        writer.writerow([i, str(texts[i]), labels[i], int(preds[i]), scores[i]])

def main():
    parser = argparse.ArgumentParser(description='Description of your script')
    parser.add_argument('--input_path', help='Help message for arg_name')
    parser.add_argument('--output_dir', help='Help message for arg_name')
    parser.add_argument('--output_name', help='Help message for arg_name')
    parser.add_argument('--template', help='Help message for arg_name')
    parser.add_argument('--eval_report', action='store_true')
    args = parser.parse_args()
    input_path = args.input_path
    output_dir = args.output_dir
    template = args.template
    eval_report = args.eval_report
    output_path = create_output_path(output_dir, template, input_path)

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
            # if data['final_result'] == "no":
            #     labels.append(0)
            # else:
            #     labels.append(1)
            if "final_result" in data:
                if data['final_result'] == "yes":
                    labels.append(0)
                else:
                    # 让广告成为1
                    labels.append(1)
            elif "ad_classify" in data:
                if data['ad_classify'] == "1":
                    labels.append(0)
                else:
                    # 让广告成为1
                    labels.append(1)

    eval_template(eval(template), texts, labels, output_path, eval_report)
 


if __name__=='__main__':
    main()
