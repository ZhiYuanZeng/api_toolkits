'''
This file is copied and modified from open-instruct
'''

import openai
import json
from tqdm import tqdm
import time
import os
import multiprocessing
from math import sqrt

def worker(args):
    """Function to be executed in a separate process"""
    if 'result' in args:
        return args['result']
    else:
        retry_limit = args['retry_limit']
        retry_count = 0
        while retry_count < retry_limit:
            try:
                outputs = openai.ChatCompletion.create(
                    api_key=args['apikey'],
                    model=args['model'],
                    messages=args['messages'],
                    **args['others']
                )
                answer = outputs["choices"][0]["message"]["content"]
                return {'prompt': args['messages'], 'response_metadata':answer, 'id':args['id'] }
            except Exception as e:
                print(e)
                if isinstance(e,openai.error.InvalidRequestError):
                    break
                retry_count += 1
                print(f"Error while requesting OpenAI API.")
                print(f"Sleep for {30*retry_count} seconds.")
                time.sleep(30*retry_count)
                print(f"Retry for the {retry_count} time.")

        if retry_count == retry_limit:
            print("Failed to get response from OpenAI API after {retry_limit} retries.")
            # raise RuntimeError(f"Failed to get response from OpenAI API after {retry_limit} retries.")

def gen_query(engine, instances_generator, existing_data, retry_limit, apikeys, **completion_kwargs):
    num_keys = len(apikeys)
    query_idx = 0
    for i,x in enumerate(instances_generator):
        if existing_data is not None and len(existing_data)>0 and x["id"] in existing_data:
            yield {'result': existing_data[x["id"]]} # write to file again
        elif len(x['prompt'].split())>1500:
            # 当文本数据超过1500时，直接抛弃，可优化
            yield {'result': None} # skip
        else:
            apikeys_index = query_idx % num_keys
            query_idx+=1
            messages = [{"role": "user", "content": x["prompt"]}]
            yield {
                'model': engine,
                'messages': messages,
                'apikey': apikeys[apikeys_index], 
                'id': i,
                'retry_limit': retry_limit,
                'others':completion_kwargs
            }



def query_chatgpt_and_save_results(
        apikeys, 
        engine, 
        instances_generator, 
        instances_number, 
        post_function=None,
        output_path=None, 
        num_processes=10, 
        retry_limit=5, 
        reuse_existing_outputs=True, 
        **completion_kwargs):
    '''
    Query OpenAI chat model and save the results to output_path.
    `instances` is a list of dictionaries, each dictionary contains a key "prompt" and a key "id".
    '''
    def write_buffer(buffer, fout):
        if fout is not None:
            for d in buffer:
                fout.write(json.dumps(d) + "\n")
                fout.flush()

    # load from existing
    existing_data = {}
    if reuse_existing_outputs and output_path is not None and os.path.exists(output_path):
        with open(output_path, "r") as f:
            for line in f:
                instance = json.loads(line)
                existing_data[instance["id"]] = instance
        print(f'load {len(existing_data)} examples from existing processed data........................')

    # set completion_kwargs
    if "temperature" not in completion_kwargs:
        completion_kwargs["temperature"] = 0.0

    pool = multiprocessing.Pool(processes=num_processes)
    results = pool.imap_unordered(worker, gen_query(
        engine, instances_generator, existing_data, retry_limit, apikeys, **completion_kwargs))
    
    buffer = []
    buffer_size = 10

    if output_path is not None:
        fout = open(output_path, 'w')
    else:
        fout = None

    outputs = []
    for result in tqdm(results, total=instances_number):
        if result is not None:
            output = post_function(result)
            if output is not None:
                outputs.append(output)
                buffer.append(output)
        if len(buffer)>buffer_size:
            write_buffer(buffer, fout)
            buffer=[]
    if len(buffer)>0:
        write_buffer(buffer, fout)
    
    if fout is not None:
        fout.close()
    return outputs

def query_chatgpt(
        apikeys, 
        engine, 
        instances_generator, 
        instances_number, 
        post_function=None, 
        existing_data=None, 
        num_processes=10, 
        retry_limit=5, 
        **completion_kwargs):
    '''
    Query OpenAI chat model and process the results with post_function
    `instances` is a list of dictionaries, each dictionary contains a key "prompt" and a key "id".
    '''

    # load from existing

    # set completion_kwargs
    if "temperature" not in completion_kwargs:
        completion_kwargs["temperature"] = 0.0
    pool = multiprocessing.Pool(processes=num_processes)
    # numbers = [1, 2, 3, 4, 5]
    # results = pool.imap_unordered(print, numbers)
    outputs = []
    results = pool.imap_unordered(worker, gen_query(engine, instances_generator, existing_data, retry_limit, apikeys, **completion_kwargs))
    for result in tqdm(results, total=instances_number):
        if result is not None:
            outputs.append(post_function(result))
    return outputs