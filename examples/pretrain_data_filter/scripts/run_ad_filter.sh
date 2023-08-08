export PYTHONPATH=${PYTHONPATH}:../../

# 广告:非广告=77:72 
# python run_ad_filter.py --input_path ../../data/ad_plus_norm_data.jsonl --output_dir ../../output/ --template "ad_filter_template2" --eval_report


python run_ad_filter.py --input_path ../../data/ad_plus_norm_0808_data.jsonl --output_dir ../../output/ --template "ad_filter_template3" --eval_report