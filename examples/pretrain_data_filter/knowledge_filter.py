import json
import re
from pipeline import BasePipeline

template1 = """
Given a document, analyze and determine whether it can be classified as information-intensive. Provide a score scale (1-10), with 1 being "Low", 5 being "middle" and 10 being "High". You can only provide the score and do not output other things.

{}
"""

template2 = """
Given a document, analyze and determine whether it can be classified as knowledge-intensive. Provide a score scale (1-10), with 1 being "Low", 5 being "middle" and 10 being "High". You can only provide the score and do not output other things.

{}
"""

template3 = """
Given a document, analyze and determine its level of knowledge-intensity. A knowledge-intensive document typically goes beyond surface-level information, providing in-depth explanations, citations to credible sources, and exploration of complex concepts. It relies on evidence-based reasoning, technical language, and may cover a wide range of related topics.

To determine the document's knowledge-intensity, consider the following factors and rate each on a scale of 1 to 5, with 1 being "Low" and 5 being "High":

1. Depth and Complexity: Does the document delve into complex concepts, theories, and ideas, providing detailed explanations and analyses?

2. Citations and References: Are there citations and references to reputable sources, academic papers, or expert opinions to support the claims and arguments made in the document?

3. Technical Language: Does the document employ technical jargon, specialized terminology, or discipline-specific language appropriate for the subject matter?

4. Research and Empirical Evidence: Does the document include references to research studies, experiments, or empirical evidence to back up its assertions?

5. Historical Context: Does the document explore the historical development of the topic or trace its evolution over time, demonstrating a comprehensive understanding?

6. Educational or Academic Context: Is the document sourced from reputable educational institutions, academic journals, or published books by established authors?

7. Breadth of Coverage: Does the document cover a wide range of related concepts, providing a comprehensive overview of the subject matter?

8. Problem-Solving and Critical Thinking: Does the document engage in problem-solving, critical analysis, and logical reasoning?

9. Original Research or Contributions: Does the document present original research findings, new insights, or innovative contributions to a field?

10. Audience and Purpose: Consider the intended audience and purpose of the document. Does it target experts, researchers, or academics, aiming to advance knowledge or contribute to a scholarly field?

Here is the document you need to justify:
{}

Provide a overall score to determine whether it can be classified as knowledge-intensive, which scale (1-10), with 1 being "Low", 5 being "middle" and 10 being "High". You can only provide the overall score and do not output other things. 
""",

"""
Given a document, analyze and determine whether it can be classified as information-intensive. Your judgement should not be too strict, the informative document can be a news talking about events or even a story. Provide a score scale (1-10), with 1 being "Low", 5 being "middle" and 10 being "High". You can only provide the score and do not output other things.

{}
"""

def parse_func(input_string):
    # Define the regular expression pattern for both float and integer numbers
    number_pattern = r'[-+]?\d*\.\d+|\d+'

    # Use re.findall() to find all occurrences of the numbers in the string
    numbers = re.findall(number_pattern, input_string)

    # Convert the found strings to actual numbers
    numbers = [float(number) if '.' in number else int(number) for number in numbers]

    return numbers[0]

class KnowledgeFilter(BasePipeline):
    @classmethod
    def build_filter(cls, template:str):
        return cls(template, parse_func)