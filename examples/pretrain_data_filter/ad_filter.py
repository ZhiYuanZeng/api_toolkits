import json
import re
from pipeline import BasePipeline

template1 = """
Given a document, analyze and determine whether it can be classified as advertisement. Provide a score scale (1-10), with 1 being "Low", 5 being "middle" and 10 being "High". You can only provide the score and do not output other things.

{}
"""



def parse_func(input_string):
    # Define the regular expression pattern for both float and integer numbers
    number_pattern = r'[-+]?\d*\.\d+|\d+'

    # Use re.findall() to find all occurrences of the numbers in the string
    numbers = re.findall(number_pattern, input_string)

    # Convert the found strings to actual numbers
    numbers = [float(number) if '.' in number else int(number) for number in numbers]

    return numbers[0]

class AdFilter(BasePipeline):
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
            print(f'parsing error ({e}), here is the raw response: ...............')
            print(gpt_response)
            return None
            # raise e
        
        # hard code, threshold can be decided by metrics
        thresh = 6
        # 对外输出的0,1标签，保持0为负样本，1为正样本
        return {'output': int(data<thresh), "score": data, 'id':gpt_response['id']}