export PYTHONPATH=${PYTHONPATH}:../../
# demo
# python run_porn_filter.py --input_path ../../data/pornographic_result_demo.jsonl --output_dir ../../pron_filter_output/ --template "pornographic_filter_template1" --eval_report --truncate

# python run_porn_filter.py --input_path ../../data/pornographic_result_2400.jsonl --output_dir ../../pron_filter_output/ --template "pornographic_filter_template1" --eval_report --truncate

# python run_porn_filter.py --input_path ../../data/pornographic_result_2400.jsonl --output_dir ../../pron_filter_output/ --template "pornographic_filter_template2" --eval_report



#python run_porn_filter.py --input_path ../../data/pornographic_result_2400_sample0.1.jsonl --output_dir ../../pron_filter_output/ --template "pornographic_filter_template2" --eval_report --model_name "gpt-4" --truncate --truncate_nums 8192




## 10%采样
# gpt3.5配置 
# python run_porn_filter.py --input_path ../../data/pornographic_result_2400_sample0.1.jsonl --output_dir ../../pron_filter_output/ --template "pornographic_filter_template1" --eval_report --model_name "gpt-3.5-turbo" --truncate --truncate_nums 4096

# 
# python run_porn_filter.py --input_path ../../data/pornographic_result_2400_sample0.1.jsonl --output_dir ../../pron_filter_output/ --template "pornographic_filter_template2" --eval_report --model_name "gpt-3.5-turbo" --truncate --truncate_nums 4096

# gpt4 配置
# python run_porn_filter.py --input_path ../../data/pornographic_result_2400_sample0.1.jsonl --output_dir ../../pron_filter_output/ --template "pornographic_filter_template1" --eval_report --model_name "gpt-4" --truncate --truncate_nums 8192

# perspective
# output_dir=../../pron_filter_output/
# python run_porn_filter.py --input_path ../../data/pornographic_result_2400_sample0.1.jsonl --output_dir ${output_dir}  --template "pornographic_filter_template1" --eval_report --model_name "perspective" 2>&1 | tee -a ${output_dir}/perspective_log.txt


# 全量
# gpt3.5配置 
# python run_porn_filter.py --input_path ../../data/pornographic_result_2400.jsonl --output_dir ../../pron_filter_output/ --template "pornographic_filter_template1" --eval_report --model_name "gpt-3.5-turbo" --truncate --truncate_nums 4096

# python run_porn_filter.py --input_path ../../data/pornographic_result_2400.jsonl --output_dir ../../pron_filter_output/ --template "pornographic_filter_template2" --eval_report --model_name "gpt-3.5-turbo" --truncate --truncate_nums 4096

# gpt4 配置 
# python run_porn_filter.py --input_path ../../data/pornographic_result_2400.jsonl --output_dir ../../pron_filter_output/ --template "pornographic_filter_template1" --eval_report --model_name "gpt-4" --truncate --truncate_nums 8192

# perspective
output_dir=../../pron_filter_output/
python run_porn_filter.py --input_path ../../data/pornographic_result_2400.jsonl --output_dir ${output_dir}  --template "pornographic_filter_template1" --eval_report --model_name "perspective" 2>&1 | tee -a ${output_dir}/perspective_full_log.txt
# 

# demo
# gpt3.5配置 
#python run_porn_filter.py --input_path ../../data/pornographic_result_demo.jsonl --output_dir ../../pron_filter_output/ --template "pornographic_filter_template1" --eval_report --model_name "gpt-3.5-turbo" --truncate --truncate_nums 4096

# python run_porn_filter.py --input_path ../../data/pornographic_result_demo.jsonl --output_dir ../../pron_filter_output/ --template "pornographic_filter_template2" --eval_report --model_name "gpt-3.5-turbo" --truncate --truncate_nums 4096

# gpt4配置
# python run_porn_filter.py --input_path ../../data/pornographic_result_demo.jsonl --output_dir ../../pron_filter_output/ --template "pornographic_filter_template1" --eval_report --model_name "gpt-4" --truncate --truncate_nums 8192 

# # perspective
# python run_porn_filter.py --input_path ../../data/pornographic_result_demo.jsonl --output_dir ../../pron_filter_output/ --template "pornographic_filter_template1" --eval_report --model_name "perspective"

