import json
import os
from run_rte import read_data as read_rte_data
from run_cb import read_data as read_cb_data

template_rte="""Problem: "{}" Using only the above description and what you know about the world, is "{}" definitely correct? Yes or no? Let's think step by step to make sure the answer is correct."""

template_cb="""{} Based on the previous passage, is it true that "{}" Let's think step by step to make sure the answer is correct."""
def concate_rte_example():
    texts, answers =  read_rte_data()
    prompts = [template_rte.format(*t) for t in texts]
    
    with open('rte2.out', 'r')  as f, open('rte_chatgpt2.jsonl', 'w') as fo:
        for l in f:
            data = json.loads(l)        
            solution = data['output']
            id = data['id']
            question = prompts[int(id)]
            concate_example = {
                'prompt': question,
                'output': solution
            }
            fo.write(json.dumps(concate_example)+'\n')

def concate_cb_example():
    texts, answers =  read_cb_data()
    prompts = [template_cb.format(*t) for t in texts]
    
    with open('cb2.out', 'r')  as f, open('cb_chatgpt2.jsonl', 'w') as fo:
        for l in f:
            data = json.loads(l)        
            solution = data['output']
            id = data['id']
            question = prompts[int(id)]
            concate_example = {
                'prompt': question,
                'output': solution
            }
            fo.write(json.dumps(concate_example)+'\n')

# concate_rte_example()
concate_cb_example()