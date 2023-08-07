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