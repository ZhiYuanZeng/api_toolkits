from pipeline import BasePipeline
import re

template1 = """
Assume you are a pre-trainer of an artificial intelligence language model. You are now examining a piece of text data scraped from the internet. Your task is to give a score to judge whether this data is suitable for training a large language model.

Here is the data you need to evaluate:

{}

When making a decision, please consider the following points:
1. Language quality: Does the data have good grammatical structure and clear context?
2. Data quality: Does the data contain meaningful content? Does it provide useful information?
3. Noise level: Does the data contain too many errors, irrelevant information, or spam?

Based on the above criteria, would you choose this piece of data for pre-training? Please only answer yes or no, do not output other things
"""

template2 = """
Assume you are a pre-trainer of an artificial intelligence language model. You are now examining a piece of text data scraped from the internet. Your task is to decide whether this data is suitable for training a large language model.

Here is the data you need to evaluate:

{}

When making a decision, please consider the following points:
1. Language quality: Does the data have good grammatical structure and clear context?
2. Information quality: Does the data contain meaningful content? Does it provide useful information?
3. Coherence level: Is the content of data coherent and relevant in context?
4. Noise level: Does the data contain too many errors, irrelevant information, or spam? 
5. Safety level: Does the data contian toxic or illegal information? Does the data contain advertisement?

Based on the above criteria, would you choose this piece of data for pre-training? Please only answer yes or no, do not output other things
"""

template3 = """
Assume you are a pre-trainer of an artificial intelligence language model. You are now examining a piece of text data scraped from the internet. Your task is to decide whether this data is suitable for training a large language model.

Here is the data you need to evaluate:

{}

There are 5 criterions that you need to consider:
1. Language quality: Does the data have good grammatical structure and clear context?
2. Information quality: Does the data contain meaningful content? Does it provide useful information?
3. Coherence level: Is the content of data coherent and relevant in context?
4. Noise level: Does the data contain too many errors, irrelevant information, or spam? 
5. Safety level: Does the data contian toxic or illegal information? Does the data contain advertisement?

You need to judge whether the data is suitable for training in terms of each criteria and give a overall score. For example:
Language quality: score1
Information quality: score2
Coherence level: score3
Noise level: score4
Safety level: score5
overall: overall_score

Each score (including overall score) should vary from -1 to 1. Just output the scores, do not output other things.
"""

# order criterions, remove typos, score border explaination
template4="""
Assume you are a pre-trainer of an artificial intelligence language model. You are now examining a piece of text data scraped from the internet. Your task is to decide whether this data is suitable for training a large language model.

Here is the data you need to evaluate:

{}

There are 5 criteria that you need to consider. They are listed below in order of importance:

Safety level: Does the data contain toxic, harmful, or illegal information such as gambling, pornography, or advertisement?
Coherence level: Is the content of the data coherent and relevant in context?
Noise level: Does the data contain too many errors, irrelevant information, or spam?
Information quality: Does the data contain meaningful content? Does it provide useful information?
Language quality: Does the data have good grammatical structure and clear context?

You need to judge whether the data is suitable for training in terms of each criterion and give an overall score. For example:
Safety level: score1
Coherence level: score2
Noise level: score3
Information quality: score4
Language quality: score5
Overall: overall_score

Each score (including overall score) should vary from -1 to 1. If you are confident that the data is of high/low quality, the score should be close to 1/-1. If you are uncertain, the score should be close to 0.
Just output the scores, do not output any other text.
"""

# explain score border for each criterion
template5 = """
Assume you are a pre-trainer of an artificial intelligence language model. You are now examining a piece of text data scraped from the internet. Your task is to decide whether this data is suitable for training a large language model.

Here is the data you need to evaluate:

{}

There are 5 criteria that you need to consider. They are listed below in order of importance, along with examples of how to apply them:

Safety level: Assess whether the data contain any toxic, harmful, or illegal information, such as gambling, pornography, or advertisement. If the text is completely safe and free of inappropriate content, score it as 1. If it contains harmful or inappropriate content, score it as -1.

Coherence level: Evaluate whether the content of the data is coherent and relevant in context. If the text flows logically and is easy to follow, score it as 1. If it's disjointed or confusing, score it as -1.

Noise level: Determine whether the data contains too many errors, irrelevant information, or spam. If the text is clean and concise without any irrelevant information or spam, score it as 1. If it's filled with errors and irrelevant content, score it as -1.

Information quality: Consider whether the data contains meaningful content or provides useful information. If it's packed with valuable and relevant information, score it as 1. If it's devoid of useful content, score it as -1.

Language quality: Judge whether the data has good grammatical structure and clear context. If the text is grammatically flawless and provides clear context, score it as 1. If it's riddled with grammatical errors and lacks context, score it as -1.

After assessing the data based on these criteria, give an overall score that reflects the cumulative suitability of the data for training. Here's how you should present your scores:

Safety level: score1
Coherence level: score2
Noise level: score3
Information quality: score4
Language quality: score5
Overall: overall_score

Each score (including overall score) should vary from -1 to 1. A score of 1 indicates a positive evaluation (i.e., the data is suitable for that criterion), a score of -1 indicates a negative evaluation (i.e., the data is unsuitable for that criterion), and a score of 0 indicates uncertainty or neutrality. Please remember to output only the scores, without any additional explanation or commentary.
"""
# a strict version of template5 to increase precision
template6="""
Assume you are a pre-trainer of an artificial intelligence language model. You are now examining a piece of text data scraped from the internet. Your task is to judge whether this data is of exceptional quality and suitability for training a large language model.

Here is the data you need to evaluate:

{}

The 5 criteria you need to consider are listed below in order of importance, along with stringent standards that must be met to achieve a high score:

Safety level: If the data is completely safe and free of inappropriate, harmful or illegal content (gambling, pornography, or advertisement), score it as 1. If there is even a slight presence of such content, score it as -1.

Coherence level: If the text flows logically, the arguments are structured, and the content is easy to follow and understand, score it as 1. If there are logical fallacies or jumps in reasoning, score it as -1.

Noise level: If the text is clean, concise, and free of any irrelevant information or spam, score it as 1. If there are any unnecessary distractions, errors, or off-topic discussions, score it as -1.

Information quality: If the data is dense with meaningful, valuable and enlightening content, score it as 1. If the information is trivial, score it as -1.

Language quality: If the data is grammatically perfect, with clear context and sophisticated vocabulary, score it as 1. If there are any language or grammatical errors, score it as -1.

After assessing the data based on these criteria, provide an overall score reflecting the cumulative suitability of the data for training. Scores should be conservative; For each criterion, only give a high score if the data strongly meets the high standards outlined:

Safety level: score1
Coherence level: score2
Noise level: score3
Information quality: score4
Language quality: score5
Overall: overall_score

Each score (including overall score) should vary from -1 to 1. A score of 1 indicates a high-quality evaluation (i.e., the data is of exceptional quality for that criterion), a score of -1 indicates that the data fails to meet the high standard for that criterion, and a score of 0 indicates that it meets some, but not all, aspects of the high standard. Please remember to output only the scores, without any additional explanation or commentary.
"""

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
            template1: parse_yes_or_no,
            template2: parse_yes_or_no,
            template3: parse_score,
            template4: parse_score,
            template5: parse_score,
            template6: parse_score,
        }
        return cls(template, pipelines[template])