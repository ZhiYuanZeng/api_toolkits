export PYTHONPATH=${PYTHONPATH}:../../

# cross validation to tune hyper-params of classifier
python run_data_filter.py --input_path ../../data/data_1.jsonl


#python run_data_filter.py --input_path ../../data/data_demo.jsonl --do_cross_validation
#python run_data_filter.py --input_path ../../data/data.jsonl --do_cross_validation