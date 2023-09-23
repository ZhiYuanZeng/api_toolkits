import json
import os
from utils import read_gpt_data

def concat_gsm8k():
    for i in range(4):
        questions, _ = read_gpt_data(f'./generated_data/gms8k_evol_instruct_epoch{i}.jsonl')
        solutions, ids = read_gpt_data(f'./generated_data/gms8k_evol_solution_epoch{i}.jsonl')   
        with open(f'./generated_data/gms8k_evol_qs_epoch{i}.jsonl', 'w') as fo:
            for s,id in zip(solutions, ids):
                q = questions[id]
                concate_example = {
                    'prompt': q,
                    'output': s
                }
                fo.write(json.dumps(concate_example)+'\n')

def concat_math():
    for i in range(4):
        questions, _ = read_gpt_data(f'./generated_data/math_evol_instruct_epoch{i}.jsonl')
        solutions, ids = read_gpt_data(f'./generated_data/math_evol_solution_epoch{i}.jsonl')   
        with open(f'./generated_data/math_evol_qs_epoch{i}.jsonl', 'w') as fo:
            for s,id in zip(solutions, ids):
                q = questions[id]
                concate_example = {
                    'prompt': q,
                    'output': s
                }
                fo.write(json.dumps(concate_example)+'\n')

concat_math()