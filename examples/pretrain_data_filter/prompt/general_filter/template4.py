# order criterions, remove typos, score border explaination
general_filter_template4 ="""
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