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