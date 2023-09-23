export PYTHONPATH=${PYTHONPATH}:../../

# cross validation to tune hyper-params of classifier
#python run_data_filter.py --input_path ../../data/data_1.jsonl



#python run_data_filter.py --input_path ../../data/data_demo.jsonl --do_cross_validation
#python run_data_filter.py --input_path ../../data/data.jsonl  --output_dir ../../general_filter_output/ --template "general_filter_template5" --do_cross_validation

# svm建模
python run_data_filter.py --input_path ../../data/data.jsonl  --output_dir ../../general_filter_output/ --template "general_filter_template5" --do_fit

# 测试
#python run_data_filter.py --input_path ../../data/data.jsonl  --output_dir ../../general_filter_output/ --template "general_filter_template5" --do_test --threshold 0.223
