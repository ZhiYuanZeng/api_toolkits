# -*- coding:utf-8 -*-

# @Author:      zp
# @Time:        2023/4/7 15:19

import openai
import json
from tqdm import tqdm
from api_utils import query_chatgpt
from apikeys import APIKEYS
import argparse
import re
import random
import json
from rouge import Rouge
import os
import time
import ast
import linecache
import random

class StoreManager():
    def __init__(self, file_path) -> None:
        self.file_path = file_path
        if os.path.exists(self.file_path):
            with open(file_path,'r') as f:
                self.examples = set([l.strip() for l in f if l.strip() != ''])
        else:
            self.examples = set()
        self.rouge = Rouge()

    def sample(self, num=10):
        return random.sample(self.examples, num)
    
    def filter(self, x):
        if not isinstance(x, str) or len(x)==0 or x in self.examples:
            return False
    
        tokens = x.split('_')

        if len(tokens) > 6:
            return False

        if len(set(tokens)) != len(tokens):
            return False
        
        return True
        
    def update(self, new_examples:list):
        for e in new_examples:
            self.examples.add(e)
        self.write(new_examples)
    
    def write(self, new_examples):
        with open(self.file_path, 'a') as f:
            f.write('\n'.join(new_examples)+'\n')

    def remove(self, examples_to_remove):
        for example in examples_to_remove:
            if example in self.examples:
                self.examples.remove(example)

def sample_lines(filename, num_lines):
    lines = []
    with open(filename, 'r') as file:
        total_lines = sum(1 for _ in file)  # Count the total number of lines in the file
        chosen_lines = random.sample(range(1, total_lines + 1), num_lines)  # Randomly choose line numbers

        for line_number in chosen_lines:
            line = linecache.getline(filename, line_number).strip()
            if line:
                lines.append(line)

    return lines

def get_odd_indices(lst):
    return lst[1::2]

def extract_function(string):
    all_functions = []
    maybe_functions_list = get_odd_indices(string.split('```'))
    for maybe_function in maybe_functions_list:
        if maybe_function.startswith('python'): # handel ```python
            maybe_function = maybe_function[6:]
        try:
            tree = ast.parse(maybe_function)

            # Traverse the AST to find function definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    function_name = node.name
                    function_body = ast.get_source_segment(string, node)
                    if not function_body.strip().endswith('"""'): # function body is not null
                        all_functions.append(function_body.strip()+'\n')
        except Exception as e:
            print('parsing error!!!!!!!!!!!!!!!!!!!!!!')
            print(e)
            print(maybe_function)
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            pass
    return all_functions

def extract_function_name(function_string):
    pattern = r'def\s+([^\s(]+)\('
    match = re.search(pattern, function_string)
    if match:
        return match.group(1)
    else:
        return None

def list_to_json_str(codes):
    codes = [{'text':c} for c in codes]
    codes = [json.dumps(c) for c in codes]
    return '\n'.join(codes)+'\n'

class GeneraterAll:
    def __init__(self, args, manager:StoreManager) -> None:
        self.args = args
        self.manager=manager
        self.template1 = \
"""
Generate a series of diverse functions implemented with python.

The *function names* should be Descriptive, Action-oriented, Specific, Consistent style
- Descriptive: The names provide an indication of what the function does or its purpose.
- Action-oriented: The names often describe an action or operation that the function performs.
- Specific: The names convey a clear idea about the expected behavior or outcome of the function.
- Consistent style: The function names use underscores to separate words, following the Python convention for function naming.

The *python implementation* should be Correct, Clarity, Self-contained and have docstring
- Correct: No syntax and logic error.
- Clarity: variable should be meaningful. The arguments of function should have type annotation, for example func(arg1: int, arg2: str)->bool
- Self-contained: No import, only use the standard python libarary

You should generate 16 diverse python functions:
# [Function0]
```
{}
```
# [Function1]
```
{}
```
# [Function2]
```
{}
```
# [Function3]
```
{}
```
# [Function4]
"""
    def generate_querys(self,):
        for i in range(self.args.instances_number):
            number_of_example = 4
            sampled_functions = sample_lines(self.args.codes_path, number_of_example)
            sampled_functions = [json.loads(func)['text'] for func in sampled_functions]
            if len(sampled_functions)!=4 or any([len(func.strip())==0 for func in sampled_functions]):
                continue
            prompt = self.template1.format(*sampled_functions)
            yield {
                'id':i,
                'prompt':prompt
            }

    def post_func(self, result):            
        s_time = time.time()
        response_metadata = result['response_metadata']
        functions = extract_function(response_metadata)
        func_names = [extract_function_name(func) for func in functions]

        filter_mask = [self.manager.filter(name) for name in func_names]
        func_names = [name for i,name in enumerate(func_names) if filter_mask[i]]
        functions = [func for i,func in enumerate(functions) if filter_mask[i]]
        if len(func_names)==0:
            return
        self.manager.update(func_names)
        with open(self.args.codes_path, 'a') as f:
            f.write(list_to_json_str(functions))
    
        e_time = time.time()
        print(f'add {sum(filter_mask)} examples, cost {e_time-s_time}s', flush=True)

class GenerateFuncName:
    def __init__(self, args, manager) -> None:
        self.args = args
        self.manager = manager
        self.template1 = \
"""
Generate 200 python function names

The *function names* should be Descriptive, Action-oriented, Specific, Consistent style
- Descriptive: The names provide an indication of what the function does or its purpose.
- Action-oriented: The names often describe an action or operation that the function performs.
- Specific: The names convey a clear idea about the expected behavior or outcome of the function.
- Consistent style: The function names use underscores to separate words, following the Python convention for function naming.

{}
"""
    def generate_querys(self):
        for i in range(self.args.instances_number):
            number_of_example = 20
            sampled_functions = sample_lines(self.args.funcnames_path, number_of_example)
            
            sampled_functions = [f'{i}. {f}' for i,f in enumerate(sampled_functions)]
            sampled_functions = '\n'.join(sampled_functions)
            prompt = self.template1.format(sampled_functions)
            yield {
                'id':i,
                'prompt':prompt
            }
    def post_func(self, result):
        response_metadata = result['response_metadata']
        func_names = response_metadata.strip().splitlines()
        try:
            func_names = [line.split('. ')[1].strip() for line in func_names]
        except Exception:
            print('parsing error!!!!!!!!!!!!!!!!!!!!!!')
            print(func_names)
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            return
        filter_mask = [self.manager.filter(name) for name in func_names]
        func_names = [name for i,name in enumerate(func_names) if filter_mask[i]]
        if len(func_names)==0:
            return
        print(func_names, flush=True)
        self.manager.update(func_names)

class GenerateFuncFromName():
    def __init__(self, args, manager:StoreManager) -> None:
        self.args = args
        self.manager = manager
        self.template1 = \
"""
Generate python function according to given function names. 
The generated function should be Correct, Clarity, Self-contained and have docstring
- Correct: No syntax and logic error. The implementations should follow the given function names.
- Clarity: variable should be meaningful. The arguments and return values of functions have type annotation.
- Self-contained: No import, only use the standard python libarary.

Wrap **each function** with ```, for example:
```
def func(args):
    pass
```

The function name and docstring  are : {}.
"""
    
    def generate_querys(self):
        number_of_example = 10
        i = 0 
        existing_function_names =[]
        with open(self.args.codes_path, 'r') as f:
            for l in f:
                existing_function = json.loads(l.strip())['text']
                existing_function_name =extract_function_name(existing_function)
                existing_function_names.append(existing_function_name)
        self.manager.remove(existing_function_names)
        print(f'remove {len(existing_function_names)} examples from store, because they already exists', flush=True)

        while len(self.manager.examples) >= number_of_example:
            sampled_functions = self.manager.sample()
            # sampled_functions = [f'{i}. {f}' for i,f in enumerate(sampled_functions)]
            # sampled_functions = '\n'.join(sampled_functions)
            prompt = self.template1.format(sampled_functions)
            yield {
                'id':i,
                'prompt':prompt
            }
            i+=1
    
    def post_func(self, result):
        response_metadata = result['response_metadata']
        functions = extract_function(response_metadata)
        func_names = [extract_function_name(func) for func in functions]

        functions_to_be_saved = []
        for func, func_name in zip(functions, func_names):
            if func_name in self.manager.examples and func_name not in functions_to_be_saved:
                functions_to_be_saved.append(func)
                self.manager.examples.remove(func_name)
        self.manager.remove(func_names)
        if len(functions_to_be_saved) != 0:
            with open(self.args.codes_path, 'a+') as f:
                f.write(list_to_json_str(functions_to_be_saved))
        print(f'save {len(functions_to_be_saved)} functions, left {len(self.manager.examples)}')

openai.api_base = "https://ai-proxy.shlab.tech/internal"
parser = argparse.ArgumentParser(description='Description of your script')
parser.add_argument('--codes_path', help='Help message for arg_name')
parser.add_argument('--funcnames_path', help='Help message for arg_name')
parser.add_argument('--instances_number', type=int, help='Help message for arg_name')
args = parser.parse_args()

   
manager = StoreManager(args.funcnames_path)
pipeline = GenerateFuncFromName(args, manager)
if isinstance(pipeline, GenerateFuncFromName):
    temperature = 0.
else:
    temperature = 1.
query_chatgpt(
    apikeys=APIKEYS, 
    engine='gpt-3.5-turbo', 
    instances_generator=pipeline.generate_querys(), 
    instances_number=args.instances_number, 
    post_function=pipeline.post_func,
    existing_data=None,
    num_processes=32,
    temperature=temperature)

