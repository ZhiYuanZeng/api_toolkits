# a strict version of template5 to increase precision
general_filter_template6 ="""
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