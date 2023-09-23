from api_utils import query_chatgpt_and_save_results
from apikeys import APIKEYS, GPT4_APIKEYS
import os
from typing import List
import tiktoken

class BasePipeline():
    def __init__(self, template, parse_func):
        self.template = template
        self.parse_func = parse_func

    def num_tokens_from_string(self, string: str, model_name: str):
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.encoding_for_model(model_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens, encoding
    
    def build_prompt(self, id, input_text, model_name="", truncate=False, truncate_nums=4096):
        def truncate_text(input_text, do_truncate):
            if do_truncate:
                template_token_nums, encoding = self.num_tokens_from_string(self.template, model_name=model_name)
                input_tokens = encoding.encode(input_text)
                # 减掉20 token裕量
                need_nums = truncate_nums-template_token_nums-20
                if need_nums < len(input_tokens):
                    input_tokens_trunc = input_tokens[:need_nums]
                    trunc_text = encoding.decode(input_tokens_trunc)
                    # 避免截断在结尾处产生奇怪的符号
                    trunc_text = trunc_text[:-3]
                    assert trunc_text in input_text
                else:
                    trunc_text = input_text
            else:
                trunc_text = input_text
            return trunc_text
        
        if isinstance(input_text, str):
            trunc_text = truncate_text(input_text, do_truncate=truncate)
            return {'id': id, 'prompt': self.template.format(trunc_text)}
        else:
            trunc_text = [truncate_text(t, do_truncate=truncate) for t in input_text]
            return {'id': id, 'prompt': self.template.format(*trunc_text)}        
    
    def post_func(self, gpt_response):
        # 后处理函数
        try:
            if 'output' in gpt_response:
                # 已经分析好的结果
                return gpt_response # already 
            data = self.parse_func(gpt_response['response_metadata'], gpt_response['id'])
        except Exception as e:  
            print(f'parsing error ({e}), here is the raw response: ...............')
            print(gpt_response)
            return None
            # raise e
        return {'output': data, 'id':gpt_response['id']}
    
    def query(
        self,
        texts,
        engine, 
        gpt_outputs_path=None, 
        num_processes=10, 
        retry_limit=5, 
        truncate=False,
        truncate_nums=4096,
        **completion_kwargs):
        if engine == 'gpt-4':
            apikeys = GPT4_APIKEYS
        else:
            apikeys = APIKEYS
        prompts = [self.build_prompt(i,t, engine, truncate, truncate_nums) for i,t in enumerate(texts)]
        assert self.template is not None
        assert self.parse_func is not None
        return query_chatgpt_and_save_results(
            apikeys=apikeys,
            engine=engine,
            instances_generator=prompts,
            instances_number=len(prompts),
            post_function=self.post_func,
            output_path=gpt_outputs_path,
            num_processes=num_processes,
            retry_limit=retry_limit,
            **completion_kwargs
        )
    
class MultipleTemplatePipeline(BasePipeline):
    def __init__(self, templates:List[str], parse_func):
        self.templates = templates
        super().__init__(None, parse_func)
    
    def build_prompt(self, id, input_text):
        raise NotImplementedError