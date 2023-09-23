from pipeline import BasePipeline

template="""
Problem: Suppose "It is part of their religion, a religion I do not scoff at as it holds many elements which match our own even though it lacks the truth of ours. At one of their great festivals they have the ritual of driving out the devils from their bodies. First the drummers come on - I may say that no women are allowed to take part in this ritual and the ladies here will perhaps agree with me that they are fortunate in that omission.". Can we infer that "no women are allowed to take part in this ritual"? Yes, no, or maybe?
Let's think step by step to make sure the answer is correct.
Answer: The statement describes a specific religious festival and ritual. It clearly states that "no women are allowed to take part in this ritual." Therefore, based on the provided information, it is accurate to infer that women are not allowed to participate in this particular ritual.
Final answer: Yes

Problem: Suppose "A: Big time there, sure is. B: It surely is. A: I don't think I'd go to work without a bulletproof vest on myself." Can we infer that "he would go to work without a bulletproof vest"? Yes, no, or maybe?
Let's think step by step to make sure the answer is correct.
Answer: The statement from A is "I don't think I'd go to work without a bulletproof vest on myself." This suggests that A believes it is necessary to wear a bulletproof vest to work, hence A would NOT go to work without a bulletproof vest. So, it is incorrect to infer that "he would go to work without a bulletproof vest". The correct inference is that "he would NOT go to work without a bulletproof vest". Therefore, the answer is NO, we cannot infer that "he would go to work without a bulletproof vest".
Final answer: No

Problem: Suppose "A: Yeah. The radio doesn't really have much news sometimes. The stations I listen to are just mainly music. B: Yeah, I think you pretty much have to listen to all news station to get any news at all. A: Yeah. Do you think that TV is, uh, pretty accurate." Can we infer that "TV is pretty accurate"? Yes, no, or maybe?
Let's think step by step to make sure the answer is correct.
Answer: The statement "TV is pretty accurate" is not explicitly confirmed or denied in the given conversation. Person A asks the question, but there is no response from Person B or any further discussion that would allow us to infer their beliefs or opinions about the accuracy of TV news. Therefore, the most appropriate answer would be "maybe," as the conversation does not provide enough information to definitively say "yes" or "no."
Final answer: Maybe

Problem: Suppose {} Can we infer that "{}"? Yes, no, or maybe?
Let's think step by step to make sure the answer is correct.
"""

class Parser:
    def __init__(self, labels) -> None:
        self.labels=labels

    def parse(self, text, example_id):
        sent = text.split('\n')[-1].lower()
        assert 'final answer' in sent, "parsing error"
        assert 'yes' in sent or 'no' in sent or 'maybe' in sent, "parsing error"
        if 'yes' in sent:
            label = 0
        elif 'no' in sent:
            label = 1
        else:
            label = 2
        
        if label == self.labels[int(example_id)]:
            return text
        else:
            raise RuntimeError(f"answer is not correct, answer:{label}, label:{self.labels[int(example_id)]}")

class Classifier(BasePipeline):
    @classmethod
    def build(cls, template, parse_func):
        return cls(template, parse_func)
    