from porn_filter import PornFilter, PerspecitivePornFilter
from prompt import pornographic_filter_template1, pornographic_filter_template2
import io
import csv
import argparse
import json
from utils import create_output_path
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score
from sklearn.metrics import precision_recall_curve
import os
from sklearn.metrics import confusion_matrix

def eval_template(template, texts, labels, output_path, eval_report=False, truncate=False, truncate_nums=4096, model_name="gpt-3.5-turbo"):
    print(f"using model :{model_name}")
    if model_name != "perspective":
        data_filter = PornFilter.build_filter(template)
        gpt_outputs = data_filter.query(
            texts=texts,
            engine=model_name, 
            gpt_outputs_path=output_path,
            num_processes=10, 
            retry_limit=5,
            temperature=0.,
            truncate=truncate,
            truncate_nums=truncate_nums)
    else:
        data_filter = PerspecitivePornFilter.build_filter("{}")
        gpt_outputs = data_filter.query(
            texts=texts,
            engine=model_name, 
            gpt_outputs_path=output_path,
            num_processes=1, 
            retry_limit=5)


    scores = [0 for _ in range(len(labels))]
    preds = [0 for _ in range(len(labels))]
    

    fo = None
    print(f'using templat:.................................', file=fo)
    print(template)
    eval_result = ["id,text,label,preds,score"]
    if model_name != "perspective":
        threshes = [ i for i in range(1,10)]
    else:
        # fixme 临时是按阈值卡，来算pr, 后续改成自动算需要的阈值
        threshes = [ i/100 for i in range(0,100)]

    print(f"output path:{output_path}")
    for thresh in threshes:
        for o in gpt_outputs:
            if o is not None:
                score = float(o['score'])
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
            report_name = os.path.join(os.path.dirname(output_path), os.path.splitext(os.path.basename(output_path))[0] + f"_thresh{thresh}_report.csv")

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
    parser.add_argument('--truncate', action='store_true')
    parser.add_argument('--truncate_nums', type=int, default=4096)
    parser.add_argument('--model_name', type=str, default="gpt-3.5-turbo", choices=['gpt-3.5-turbo', 'gpt-4', "perspective"])
    args = parser.parse_args()
    input_path = args.input_path
    output_dir = args.output_dir
    template = args.template
    eval_report = args.eval_report
    truncate_nums = args.truncate_nums
    truncate = args.truncate
    model_name = args.model_name
    output_path = create_output_path(output_dir, template, input_path, prefix=f"gpt_{model_name}_out_porn_filter_truncate{int(truncate)}")

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
            if "is_erotic" in data:

                if data['is_erotic'] == False:
                    labels.append(0)
                else:
                    # 让广告成为1
                    labels.append(1)
            else:
                assert 0
    eval_template(eval(template), texts, labels, output_path, eval_report, truncate=truncate, truncate_nums=truncate_nums, model_name=model_name)
 


if __name__=='__main__':
    main()
