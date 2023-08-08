# explain score border for each criterion
general_filter_template5 = """
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