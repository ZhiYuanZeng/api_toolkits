from pipeline import BasePipeline

template = """
Your task is to translate a low-quality document that may be noisy, toxic, or useless to high-quality one that is clean, safe, and can be used as the training corpus of language models. The text may contain poor grammar, unnecessary profanity, irrelevant content, or other detrimental qualities. It's important to maintain the original intent of the text, but make it suitable and effective for language model training.

You should take the following actions based on the text:

1. If the text can be improved and translated to high-quality text, do so. Your answer should then contain a 'yes' along with the improved text.

2. If the text is too messy, unintelligible, or otherwise impossible to improve to high-quality standards, respond with a 'no' and provide a reason.

3. If the text is already of high-quality and does not require translation or improvement, respond with a 'no' and provide a reason.

Remember, your task is to improve and translate, not to add new content or conclusions.

Here is the text to be improved:

{}

You must format your answer as the xml style, in one of the following ways:

1. Yes\nThis is the improved text...
2. No\nThis is the reason...
"""

def parse(raw_text):
    text = '\n'.join(raw_text.split('\n')[1:])
    text = text.strip()
    if raw_text.lower().startswith('yes'):
        return {'text': text, 'label':1}
    elif raw_text.lower().startswith('no'):
        return {'text': text, 'label':-1}
    else:
        raise Exception(f'response must be yes or no')

class DataRewritter(BasePipeline):
    @classmethod
    def build_filter(cls):
        return cls(template, parse)