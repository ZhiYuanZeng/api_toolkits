import json
import re
from pipeline import BasePipeline
from apikeys import PERSPECTIVE_APIKEYS
from api_utils import query_perspective_and_save_results
def parse_func(input_string):
    if "score" not in input_string.lower() and not input_string.isdigit() :
        # gpt3.5-turbo下 有些case不跟随指令，返回一堆生成成果, 这种case忽略返回
        # gpt4下会直接返回数字
        return None

    # Define the regular expression pattern for both float and integer numbers
    number_pattern = r'[-+]?\d*\.\d+|\d+'

    # Use re.findall() to find all occurrences of the numbers in the string
    numbers = re.findall(number_pattern, input_string)

    # Convert the found strings to actual numbers
    numbers = [float(number) if '.' in number else int(number) for number in numbers]
    if len(numbers) == 0:
        return None
    else:
        return numbers[0]

class PornFilter(BasePipeline):
    @classmethod
    def build_filter(cls, template:str):
        return cls(template, parse_func)

    def post_func(self, gpt_response):
        # 后处理函数
        try:
            if 'output' in gpt_response:
                # 已经分析好的结果
                return gpt_response # already parsed
            data = self.parse(raw_text=gpt_response['response_metadata'])
        except Exception as e:
            import pdb
            pdb.set_trace()
            print(f'parsing error ({e}), here is the raw response: ...............')
            print(gpt_response)
            return 
            
            # raise e
        
        # hard code, threshold can be decided by metrics
        thresh = 5

        if data is not None:
            # 对外输出的0,1标签，保持0为负样本，1为正样本
            return {'output': int(data<thresh), "score": data, 'id':gpt_response['id'], "raw_response": gpt_response['response_metadata']}
        else:
            # 无效输出下不过滤，给正样本标签
            return {'output': 1, "score": -100, 'id':gpt_response['id'], "raw_response": gpt_response['response_metadata']}


def perspective_parse_func(input_string):
    return float(input_string)

class PerspecitivePornFilter(BasePipeline):
    @classmethod
    def build_filter(cls, template:str):
        return cls(template, perspective_parse_func)

    def build_prompt(self, id, input_text, model_name="", truncate=False, truncate_nums=4096):
        # perspective目前支持20480
        # Comment text was too many bytes. Value (50149) exceeded limit (20480).". Details: "Comment text was too many bytes. Value (50149) exceeded limit (20480
        trunc_text = input_text[:20200]
        return {'id': id, 'prompt': self.template.format(trunc_text)}
        
     
    def post_func(self, gpt_response):
        # 后处理函数
        try:
            if 'output' in gpt_response:
                # 已经分析好的结果
                return gpt_response # already parsed
            data = self.parse(raw_text=gpt_response['response_metadata'])
        except Exception as e:
            import pdb
            pdb.set_trace()
            print(f'parsing error ({e}), here is the raw response: ...............')
            print(gpt_response)
            return 
            
        # hard code, threshold can be decided by metrics
        thresh = 5

        if data is not None:
            # 对外输出的0,1标签，保持0为负样本，1为正样本
            return {'output': int(data<thresh), "score": data, 'id':gpt_response['id'], "raw_response": gpt_response['response_metadata']}
        else:
            # 无效输出下不过滤，给正样本标签
            return {'output': 1, "score": -100, 'id':gpt_response['id'], "raw_response": gpt_response['response_metadata']}


    def query(
        self,
        texts,
        engine, 
        gpt_outputs_path=None, 
        num_processes=10, 
        retry_limit=5):
        apikeys = PERSPECTIVE_APIKEYS
        prompts = [self.build_prompt(i,t, engine, False, 100000) for i,t in enumerate(texts)]
        assert self.template is not None
        assert self.parse_func is not None
        return query_perspective_and_save_results(
            apikeys=apikeys,
            engine=engine,
            instances_generator=prompts,
            instances_number=len(prompts),
            post_function=self.post_func,
            output_path=gpt_outputs_path,
            num_processes=num_processes,
            retry_limit=retry_limit,
        )

    def parse(self, raw_text):
        return self.parse_func(raw_text)

    def post_func(self, gpt_response):
        # 后处理函数
        try:
            if 'output' in gpt_response:
                # 已经分析好的结果
                return gpt_response # already parsed
            data = self.parse(raw_text=gpt_response['response_metadata'])
        except Exception as e:
            print(f'parsing error ({e}), here is the raw response: ...............')
            print(gpt_response)
            return None
            # raise e     
        # hard code, threshold can be decided by metrics
        thresh = 0.5
        # 对外输出的0,1标签，保持0为负样本，1为正样本
        return {'output': int(data<thresh), "score": data, 'id': gpt_response['id']}    