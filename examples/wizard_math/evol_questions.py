from pipeline import BasePipeline, MultipleTemplatePipeline
import json
import os
from copy import deepcopy
import random

template1 = """
Given a mathematical question, you need to propose a new question by changing some numbers of the original question. Remember to make sure that the new question is sovable.
Just output new questions, do not output other things.
question: {}
New question:
"""
template2 = """
Given a mathematical question, you need to propose a new question by changing the topic or content of the original question but make sure that the new question shares a similar solution with the original quesiton. Remember to make sure that the new question is sovable.
Just output new questions, do not output other things.
question: {}
New question:
"""
template3 = """
Given a mathematical question, you need to propose a new question by making the original question more complicated by adding constraints, concretizing and increasing reasoning steps. Remember to make sure that the new question is sovable.
Just output new questions, do not output other things.
question: {}
New question:
"""

def parse(text, *args, **kwargs):
    print('gpt output:', text)
    return text

class EvolPipeline(MultipleTemplatePipeline):
    @classmethod
    def build(cls):
        return cls([template1, template2, template3], parse)

    def build_prompt(self, id, input_text):
        i = random.sample([0,1,2,2,2,2], k=1)[0]
        if i == 0:
            template = template1
        elif i == 1:
            template = template2
        else:
            template = template3
        print(f'using template: {i}')
        if isinstance(input_text, str):
            return {'id': id, 'prompt': template.format(input_text)}
        else:
            return {'id': id, 'prompt': template.format(*input_text)}

def last_boxed_only_string(string):
    idx = string.rfind("\\boxed")
    if idx < 0:
        idx = string.rfind("\\fbox")
        if idx < 0:
            return None

    i = idx
    right_brace_idx = None
    num_left_braces_open = 0
    while i < len(string):
        if string[i] == "{":
            num_left_braces_open += 1
        if string[i] == "}":
            num_left_braces_open -= 1
            if num_left_braces_open == 0:
                right_brace_idx = i
                break
        i += 1
    
    if right_brace_idx == None:
        retval = None
    else:
        retval = string[idx:right_brace_idx + 1]
    
    return retval

def remove_boxed(s):
    left = "\\boxed{"
    try:
        assert s[:len(left)] == left
        assert s[-1] == "}"
        return s[len(left):-1]
    except:
        return None

def read_gms8k_data(data_path):
    questions, solutions, answers = [], [], []
    with open(data_path, 'r') as f:
        for l in f:
            data=json.loads(l)
            question = data['question']
            solution = data['answer']
            final_answer = solution.split('#### ')[1].replace(',', '')
            questions.append(question)
            solutions.append(solution)
            answers.append(final_answer)
    return questions, solutions, answers

def read_math_data(data_dir):
    questions = []
    solutions = []
    answers = []
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if not file.endswith('.json'):
                continue
            path=os.path.join(root, file)
            with open(path, 'r') as f:
                data=json.load(f)
                try:
                    answer = remove_boxed(last_boxed_only_string(data['solution']))
                    questions.append(data['problem'])
                    solutions.append(data['solution'])
                    answers.append(answer)
                except Exception:
                    print('parsing error:' + data['solution']) 
    return questions, solutions, answers               

if __name__=='__main__':
    # questions, _, _ = read_gms8k_data('../math_cot/gsm8k/train.jsonl')
    questions, solutions, answers = read_math_data('../math_cot/MATH/train/')
    print('number of questions: {}'.format(len(questions)))
    pipeline = EvolPipeline.build()
    new_math_data = deepcopy(questions)

    for epoch in range(4):
        gpt_outputs = pipeline.query(
            texts=new_math_data,
            engine='gpt-3.5-turbo',
            num_processes=10,
            gpt_outputs_path=f'./math_evol_instruct_epoch{epoch}.jsonl'
        )
        for i,o in enumerate(gpt_outputs):
            new_math_data[int(o['id'])] = o['output']