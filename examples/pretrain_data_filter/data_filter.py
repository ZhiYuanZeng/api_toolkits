from pipeline import BasePipeline
import re
from prompt import general_filter_template1, general_filter_template2, general_filter_template3, general_filter_template4, general_filter_template5, general_filter_template6

def parse_yes_or_no(raw_text):
    if raw_text.lower() not in ('yes', 'no'):
        raise Exception(f'response must be yes or no')
    if raw_text.lower() == 'yes':
        return 1
    else:
        return -1

def parse_score(raw_text):
    scores = re.findall(r': ([-+]?\d*\.\d+|[-+]?\d+)', raw_text)
    scores = [float(s) for s in scores]
    return scores

class DataFilter(BasePipeline):    
    @classmethod
    def build_filter(cls, template:str):
        pipelines = {
            general_filter_template1: parse_yes_or_no,
            general_filter_template2: parse_yes_or_no,
            general_filter_template3: parse_score,
            general_filter_template4: parse_score,
            general_filter_template5: parse_score,
            general_filter_template6: parse_score,
        }
        return cls(template, pipelines[template])