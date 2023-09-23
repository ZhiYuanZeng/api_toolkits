import json
for epoch in range(4):
    with open(f'evol_instruct_epoch{epoch}.jsonl','r') as f1, open(f'./evol_code_epoch{epoch}_add_import.jsonl','r') as f2:
        ids1 = [json.loads(l)['id'] for l in f1]
        data = [json.loads(l) for l in f2]
        ids2 = [d['id'] for d in data]
        for i,id2 in enumerate(ids2):
            map_id = ids1[int(id2)]
            data[i]['id'] = map_id
    with open(f'evol_code_epoch{epoch}_add_import_newid.jsonl','w') as f:
        for d in data:
            f.write(json.dumps(d)+'\n')
