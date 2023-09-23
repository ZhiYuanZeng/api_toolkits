import os
import argparse
import json
import numpy as np
import random

def extract_data(text):
    try:
        data=json.loads(text)
    except Exception as e:
        print(text)
        print(e)
        return None
    prompt = data['prompt'][0]['content']
    prompt = prompt.split('[Code]')[-1].strip()
    prompt = prompt.split('```')[1]
    prompt = prompt.strip()
    
    if data['response_metadata'].lower().startswith('yes'):
        label=1
    else:
        label=0
    return {"text":prompt, "label":label}
def process_line(line):
    # Do something with each line
    print(line)

def iterate_files(directory):
    datasets = []
    for root, dirs, files in os.walk(directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            with open(file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    data = extract_data(line)
                    if data is not None:
                        datasets.append(data)
    return datasets

def process_dataset(datasets):
    def _cumulative_average(arr):
        cumsum = np.cumsum(arr)  # Calculate cumulative sum
        indices = np.arange(1, len(arr) + 1)  # Generate array of indices
        averages = cumsum / indices  # Calculate averages
        return averages

    def _len_of_text(text):
        return len(text.split('\n'))

    def _avg_len_of_dataset(dataset):
        return sum([_len_of_text(d['text']) for d in dataset])/len(dataset)
    
    # filter too short codes
    datasets = [d  for d in datasets if _len_of_text(d['text'])>4]

    positive_datasets = [d for d in datasets if d['label']==1]
    negative_datasets = [d for d in datasets if d['label']==0]

    # balance code lengths
    positive_avg_len = _avg_len_of_dataset(positive_datasets)
    negative_avg_len = _avg_len_of_dataset(negative_datasets)
    assert negative_avg_len > positive_avg_len

    ordered_neg_datasets = sorted(negative_datasets, key = lambda item:_len_of_text(item['text']))
    cumavg_neg_len = _cumulative_average([_len_of_text(d['text']) for d in ordered_neg_datasets])

    split_index = 0
    for x in cumavg_neg_len.tolist():
        split_index+=1
        if x>positive_avg_len:
            break

    ordered_neg_datasets = ordered_neg_datasets[:split_index]
    new_neg_avg_len = _avg_len_of_dataset(ordered_neg_datasets)
    print('len of positive samples:{}'.format(len(positive_datasets)))
    print('len of negative samples:{}'.format(len(ordered_neg_datasets)))

    print('avg len of positive samples:{}'.format(positive_avg_len))
    print('avg len of negative samples:{}'.format(new_neg_avg_len))

    positive_datasets.extend(ordered_neg_datasets) # concate
    
    return positive_datasets

def split_dataset(dataset, train_ratio, val_ratio):
    # Shuffle the dataset
    random.shuffle(dataset)

    # Calculate the number of samples for each set
    total_samples = len(dataset)
    train_samples = int(total_samples * train_ratio)
    val_samples = int(total_samples * val_ratio)

    # Split the dataset into train, validation, and test sets
    train_set = dataset[:train_samples]
    val_set = dataset[train_samples:train_samples + val_samples]
    test_set = dataset[train_samples + val_samples:]

    return train_set, val_set, test_set

def save_datasets(train_set, val_set, test_set, file_prefix):
    # Save training set
    train_file = file_prefix + '.train.json'
    with open(train_file, 'w') as f:
        json.dump(train_set, f)

    # Save validation set
    val_file = file_prefix + '.valid.json'
    with open(val_file, 'w') as f:
        json.dump(val_set, f)

    # Save test set
    test_file = file_prefix + '.test.json'
    with open(test_file, 'w') as f:
        json.dump(test_set, f)

def main():
    parser = argparse.ArgumentParser(description='Iterate over lines in files in a directory.')
    parser.add_argument('--input_dir', help='Directory containing the files.')
    parser.add_argument('--dataset_prefix', help='Directory containing the files.')
    args = parser.parse_args()

    datasets = iterate_files(args.input_dir)
    datasets = process_dataset(datasets)
    train_set, valid_set, test_set = split_dataset(datasets, train_ratio=0.95, val_ratio=0.025)
    save_datasets(train_set, valid_set, test_set, file_prefix=args.dataset_prefix)

if __name__ == '__main__':
    main()
