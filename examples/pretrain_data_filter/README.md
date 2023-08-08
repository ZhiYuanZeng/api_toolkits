# Pretrain data annotation with chatgpt
## Pretrain data filter
```bash
export PYTHONPATH=${PYTHONPATH}:../../

# cross validation to tune hyper-params of classifier
python run_data_filter.py --input_path ./data.jsonl --do_cross_validation

# fit gpt scores with svc classifier and save model
python run_data_filter.py --input_path ./data.jsonl --do_fit

# load model and test or predict
python run_data_filter.py --input_path ./data.jsonl --do_test
```

## Rewrite data
```bash
export PYTHONPATH=${PYTHONPATH}:../../
# refine negative but safe data
python run_data_rewrite.py --do_refine --gpt_feature_path gptoutputs_template5_gpt-3.5-turbo.jsonl --text_path data.jsonl --refined_text_path refined_template5_gpt-3.5-turbo.jsonl

# evaluate refinement
python run_data_rewrite.py --do_test --refined_text_path refined_template5_gpt-3.5-turbo.jsonl
```


## 广告检测
```bash
cd examples/pretrain_data_filter
bash scripts/run_ad_filter.sh
```