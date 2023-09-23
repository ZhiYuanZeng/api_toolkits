from cb_generator import Classifier, Parser, template
from datasets import load_dataset

def read_data():
    ds = load_dataset('super_glue', 'cb')
    text_pairs, answers = [], []
    for e in ds['train']:
        text_pairs.append((e['premise'], e['hypothesis']), )
        answers.append(e['label'])
    return text_pairs, answers

if __name__=='__main__':
    texts, answers =  read_data()
    parser = Parser(answers)
    classifier = Classifier.build(template, parser.parse)

    classifier.query(
        texts=texts,
        engine='gpt-3.5-turbo', 
        gpt_outputs_path='./cb2.out',
        num_processes=32, 
        retry_limit=5,
        temperature=1.)