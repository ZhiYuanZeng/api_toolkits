from pipeline import BasePipeline
import json
import ast
import re
from copy import deepcopy

template = """
Please increase the difficulty of the given function name and function docstring a
bit. You can increase the difficulty using, but not limited to, the following
methods:
- Add new constraints and requirements to the original problem, adding
approximately 10 additional words.
- Replace a commonly used requirement in the programming task with a less
common and more specific one.
- If the  original problem can be solved with only a few logical steps,
please add more reasoning steps.
- Provide a piece of erroneous code as a reference to increase
misdirection.
- Propose higher time or space complexity requirements, but please refrain
from doing so frequently.

NOTE (important): the function name should not be too long (no more than 6 words).

The function name: {}
The function docstring: {}

You need to output the new function name and doctsring in two lines. For example:
new function name:
new docstring:
"""

def parse(text, *args, **kwargs):
    assert 'function name' in text.lower() and 'docstring' in text.lower()
    function_name, docstring = None, None
    function_name_match = re.search(r'function name:\s*(\w+)', text)
    docstring_match = re.search(r'docstring:\s*(.*)', text, re.DOTALL)

    if function_name_match:
        function_name = function_name_match.group(1)
        # print(f"Function Name: {function_name}")
    else:
        raise RuntimeError("Function name not found in text.")

    if docstring_match:
        docstring = docstring_match.group(1).strip()
        # print(f"Docstring: {docstring}")
    else:
        raise RuntimeError("Docstring not found in text.")

    return {'func_name': function_name, 'docstring':docstring}

class EvolPipeline(BasePipeline):
    @classmethod
    def build(cls):
        return cls(template, parse)

def extract_function_info_from_string(source_code):
    # Parse the source code into an abstract syntax tree (AST)
    try:
        parsed_ast = ast.parse(source_code)
    except SyntaxError as e:
        print(f"Syntax error in the source code: {e}")
        return None, None

    # Find the function definition node (e.g., FunctionDef)
    for node in ast.walk(parsed_ast):
        if isinstance(node, ast.FunctionDef):
            function_name = node.name
            docstring = ast.get_docstring(node)
            return function_name, docstring

    return None, None


def read_data(function_path):
    function_names = []
    docstrings = []
    total_cnt = 0
    with open(function_path, 'r') as f:
        for l in f:
            function = json.loads(l)['text']
            function_name, docstring = extract_function_info_from_string(function)
            if function_name is not None and docstring is not None:
                function_names.append(function_name)
                docstrings.append(docstring)
            total_cnt+=1
    print(len(function_names)/total_cnt)
    return function_names, docstrings

function_names, docstrings = read_data('/mnt/petrelfs/share_data/zengzhiyuan/python_functions30k_filtered.jsonl')
pipeline = EvolPipeline.build()
funcname_docstring_pairs = list(zip(function_names, docstrings))
new_funcname_docstring_pairs =  deepcopy(funcname_docstring_pairs)
for epoch in range(4):
    gpt_outputs = pipeline.query(
        texts=new_funcname_docstring_pairs,
        engine='gpt-3.5-turbo',
        num_processes=10,
        gpt_outputs_path=f'./evol_instruct_epoch{epoch}.jsonl'
    )
    for i,o in enumerate(gpt_outputs):
        new_funcname_docstring_pairs[int(o['id'])] = (o['output']['func_name'], o['output']['docstring'])
