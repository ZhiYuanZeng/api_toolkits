from api_utils import query_chatgpt_and_save_results
from apikeys import APIKEYS, GPT4_APIKEYS
import os

class BasePipeline():
    def __init__(self, template, parse_func):
        self.template = template
        self.parse_func = parse_func

    def build_prompt(self, id, *input_text):
        return {'id': id, 'prompt': self.template.format(*input_text)}
    
    def parse(self, raw_text):
        return self.parse_func(raw_text)

    def post_func(self, gpt_response):
        try:
            if 'output' in gpt_response:
                return gpt_response # already parsed
            data = self.parse(raw_text=gpt_response['response_metadata'])
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
        **completion_kwargs):
        if engine == 'gpt-4':
            apikeys = GPT4_APIKEYS
        else:
            apikeys = APIKEYS
        prompts = [self.build_prompt(i,t) for i,t in enumerate(texts)]
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

