from pipeline import BasePipeline

template="""
Problem: "No Weapons of Mass Destruction Found in Iraq Yet." Using only the above description and what you know about the world, is "Weapons of Mass Destruction Found in Iraq." definitely correct? Yes or no?
Let's think step by step to make sure the answer is correct.
Answer: The problem statement clearly states "No Weapons of Mass Destruction Found in Iraq Yet," which implies that as of the current information available, no weapons of mass destruction have been found in Iraq. Therefore, the statement "Weapons of Mass Destruction Found in Iraq" is definitely not correct as of the current information provided. So the answer is No.
Final answer: No

Problem: "A place of sorrow, after Pope John Paul II died, became a place of celebration, as Roman Catholic faithful gathered in downtown Chicago to mark the installation of new Pope Benedict XVI." Using only the above description and what you know about the world, is "Pope Benedict XVI is the new leader of the Roman Catholic Church." definitely correct? Yes or no?
Let's think step by step to make sure the answer is correct.
Answer: The given statement refers to a transition from sorrow, following the death of Pope John Paul II, to celebration in downtown Chicago with the marking of the installation of Pope Benedict XVI. Given that the installation of a pope is a ceremony to mark the beginning of a new pope's reign, it is safe to say that Pope Benedict XVI is the new leader of the Roman Catholic Church based on this description. Therefore, the answer is yes, "Pope Benedict XVI is the new leader of the Roman Catholic Church." is definitely correct.
Final answer: Yes

Problem: "Herceptin was already approved to treat the sickest breast cancer patients, and the company said, Monday, it will discuss with federal regulators the possibility of prescribing the drug for more breast cancer patients." Using only the above description and what you know about the world, is "Herceptin can be used to treat breast cancer." definitely correct? Yes or no?
Let's think step by step to make sure the answer is correct.
Answer: The given statement indicates that Herceptin was already approved for the treatment of the sickest breast cancer patients. This clearly implies that Herceptin can be used to treat breast cancer, at least in certain cases. Therefore, the answer is yes, "Herceptin can be used to treat breast cancer." is definitely correct.
Final answer: Yes

Problem: Judie Vivian, chief executive at ProMedica, a medical service company that helps sustain the 2-year-old Vietnam Heart Institute in Ho Chi Minh City (formerly Saigon), said that so far about 1,500 children have received treatment. Using only the above description and what you know about the world, is "The previous name of Ho Chi Minh City was Saigon." definitely correct? Yes or no?
Let's think step by step to make sure the answer is correct.
Answer: Yes, the previous name of Ho Chi Minh City was Saigon. This is a well-documented fact in history. In 1976, following the end of the Vietnam War and the reunification of North and South Vietnam, Saigon, the capital of South Vietnam, was renamed Ho Chi Minh City in honor of the late North Vietnamese leader Ho Chi Minh. This renaming symbolized the reunification of the country under a communist government. This fact is indirectly confirmed in your provided text, which notes Ho Chi Minh City as "formerly Saigon."
Final answer: Yes

Problem: "{}" Using only the above description and what you know about the world, is "{}" definitely correct? Yes or no?
Let's think step by step to make sure the answer is correct.
"""

class Parser:
    def __init__(self, labels) -> None:
        self.labels=labels

    def parse(self, text, example_id):
        sent = text.split('\n')[-1].lower()
        assert 'final answer' in sent, "parsing error"
        assert 'yes' in sent or 'no' in sent, "parsing error"
        if 'yes' in sent:
            label = 0
        else:
            label = 1
        if label == self.labels[int(example_id)]:
            return text
        else:
            raise RuntimeError(f"answer is not correct, answer:{label}, label:{self.labels[int(example_id)]}")

class Classifier(BasePipeline):
    @classmethod
    def build(cls, template, parse_func):
        return cls(template, parse_func)
    