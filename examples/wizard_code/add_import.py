import json

def add_import(file_path, output_path):
    all_new_lines = []
    with open(file_path, 'r') as f:
        for l in f:
            data = json.loads(l)
            if 'List[' in l:
                data['output'] = 'from typing import List\n'+data['output']
            if 'Tuple[' in l:
                data['output'] = 'from typing import Tuple\n'+data['output']
            all_new_lines.append(json.dumps(data))

    with open(output_path, 'w') as f:
        for l in all_new_lines:
            f.write(l+'\n')

add_import('./evol_code_epoch0.jsonl', './evol_code_epoch0_add_import.jsonl')
add_import('./evol_code_epoch1.jsonl', './evol_code_epoch1_add_import.jsonl')
add_import('./evol_code_epoch2.jsonl', './evol_code_epoch2_add_import.jsonl')
add_import('./evol_code_epoch3.jsonl', './evol_code_epoch3_add_import.jsonl')