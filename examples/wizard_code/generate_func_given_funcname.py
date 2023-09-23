from pipeline import BasePipeline
import json
import ast
import re

template="""
Generate a python function according to given function name and doctstring. 
The generated function should be Correct, Clarity, Self-contained
- Correct: No syntax and logic error. The implementations should follow the given function names.
- Clarity: variable should be meaningful. The arguments and return values of functions have type annotation.
- Self-contained: No import, only use the standard python libarary.

The given function name is [{}]
The given docstring is [{}]
    
Wrap the function with ```, for example:
```
def func(args):`
    pass
```
"""

def get_odd_indices(lst):
    return lst[1::2]

def extract_function(string, *args, **kwargs):
    all_functions = []
    all_func_names = []
    maybe_functions_list = get_odd_indices(string.split('```'))
    if len(maybe_functions_list) == 0:
        maybe_functions_list = [string,]
    for maybe_function in maybe_functions_list:
        if maybe_function.startswith('python'): # handel ```python
            maybe_function = maybe_function[6:]
        tree = ast.parse(maybe_function)

        # Traverse the AST to find function definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_name = node.name
                function_body = ast.get_source_segment(string, node)
                if not function_body.strip().endswith('"""'): # function body is not null
                    all_functions.append(function_body.strip()+'\n')
                    all_func_names.append(function_name)
    return all_func_names, all_functions

def extract_function_name(function_string):
    pattern = r'def\s+([^\s(]+)\('
    match = re.search(pattern, function_string)
    if match:
        return match.group(1)
    else:
        return None

class Parser:
    def __init__(self, func_names):
        self.func_names = func_names

    def parse(self, text, *args, **kwargs):
        func_names, functions = extract_function(text)
        for func_name, function in zip(func_names, functions):
            if func_name in self.func_names:
                return function
        raise RuntimeError("function can not be extracted")

class GenerateCodePipeline(BasePipeline):
    @classmethod
    def build(cls, template, parse_func):
        return cls(template, parse_func)

def read_data(data_path):
    func_name_doc_pairs = []
    with open(data_path, 'r') as f:
        for l in f:
            data = json.loads(l)
            func_name = data['output']['func_name']
            doc_string = data['output']['docstring']
            if func_name is not None and doc_string is not None:
                func_name_doc_pairs.append((func_name, doc_string))
    print(f'load {len(func_name_doc_pairs)} from {data_path}')
    return func_name_doc_pairs

for epoch in range(4):
    data = read_data(f'./evol_instruct_epoch{epoch}.jsonl')
    func_names = [d[0] for d in data]
    parser = Parser(func_names)
    generate_code_pipeline = GenerateCodePipeline.build(template, parser.parse)

    gpt_outputs = generate_code_pipeline.query(
        texts=data,
        engine='gpt-3.5-turbo',
        gpt_outputs_path=f'evol_code_epoch{epoch}.jsonl',
        num_processes=16
    )
