import json

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
jsonlines_file_path = 'data/data.jsonl'
json_datas = read_jsonlines_file(jsonlines_file_path)


ad_json_data = []
norm_json_data = []
for json_data in json_datas:
    get_ad = False
    for eval_data in json_data["eval_data_list"]:
        try:
            if eval_data["evaluation"]["conversation_evaluation"] is not None and "evidence" in eval_data["evaluation"]["conversation_evaluation"]:
                evidence = eval_data["evaluation"]["conversation_evaluation"]["evidence"]
            else:
                continue
        except:
            import pdb
            pdb.set_trace()
            pass

        if "广告" in evidence or "营销" in evidence:
            json_data["final_result_str"] = "no"
            json_data["final_result"] = "no"
            ad_json_data.append(json_data)
            get_ad = True
            break
    
    if get_ad == False:
        if json_data["final_result"] == "yes":
            norm_json_data.append(json_data)


# 广告集合
ad_jsonlines_file_path = 'data/ad_data.jsonl'
write_to_jsonlines_file(ad_jsonlines_file_path, ad_json_data)

# 正样本标签的集合
norm_jsonlines_file_path = 'data/norm_data.jsonl'
write_to_jsonlines_file(norm_jsonlines_file_path, norm_json_data)


