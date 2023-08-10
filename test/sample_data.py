import json
import random
def read_jsonlines_file(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            # Load each line as a JSON object and append to the data list
            data.append(json.loads(line))
    return data

def write_to_jsonlines_file(file_path, data_list):
    with open(file_path, 'w', encoding='utf-8') as file:
        for data in data_list:
            # 将每个字典转换为JSON字符串，并添加换行符
            json.dump(data, file, ensure_ascii=False)
            file.write('\n')


# 替换 'your_jsonlines_file.jsonl' 为您实际的文件路径
jsonlines_file_path = 'data/pornographic_result_2400.jsonl'
json_datas = read_jsonlines_file(jsonlines_file_path)
json_nums = len(json_datas)
sample_ratio = 0.1

json_sample_datas = random.sample(json_datas, int(json_nums*sample_ratio))
# 广告集合
ad_jsonlines_file_path = 'data/pornographic_result_2400_sample0.1.jsonl'
write_to_jsonlines_file(ad_jsonlines_file_path, json_sample_datas)
