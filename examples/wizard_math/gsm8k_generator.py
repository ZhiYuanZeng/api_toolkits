from pipeline import BasePipeline
import json
from utils import gsm8k_postprocess, read_gpt_data, read_gms8k_data

template1="""
Question: Angelo and Melanie want to plan how many hours over the next week they should study together for their test next week. They have 2 chapters of their textbook to study and 4 worksheets to memorize. They figure out that they should dedicate 3 hours to each chapter of their textbook and 1.5 hours for each worksheet. If they plan to study no more than 4 hours each day, how many days should they plan to study total over the next week if they take a 10-minute break every hour, include 3 10-minute snack breaks each day, and 30 minutes for lunch each day?
Let's think step by step
Answer:
Angelo and Melanie think they should dedicate 3 hours to each of the 2 chapters, 3 hours x 2 chapters = 6 hours total.
For the worksheets they plan to dedicate 1.5 hours for each worksheet, 1.5 hours x 4 worksheets = 6 hours total.
Angelo and Melanie need to start with planning 12 hours to study, at 4 hours a day, 12 / 4 = 3 days.
However, they need to include time for breaks and lunch. Every hour they want to include a 10-minute break, so 12 total hours x 10 minutes = 120 extra minutes for breaks.
They also want to include 3 10-minute snack breaks, 3 x 10 minutes = 30 minutes.
And they want to include 30 minutes for lunch each day, so 120 minutes for breaks + 30 minutes for snack breaks + 30 minutes for lunch = 180 minutes, or 180 / 60 minutes per hour = 3 extra hours.
So Angelo and Melanie want to plan 12 hours to study + 3 hours of breaks = 15 hours total.
They want to study no more than 4 hours each day, 15 hours / 4 hours each day = 3.75
They will need to plan to study 4 days to allow for all the time they need.
The answer is 4

Question: Mark's basketball team scores 25 2 pointers, 8 3 pointers and 10 free throws.  Their opponents score double the 2 pointers but half the 3 pointers and free throws.  What's the total number of points scored by both teams added together?
Let's think step by step
Answer:
Mark's team scores 25 2 pointers, meaning they scored 25*2= 50 points in 2 pointers.
His team also scores 6 3 pointers, meaning they scored 8*3= 24 points in 3 pointers
They scored 10 free throws, and free throws count as one point so they scored 10*1=10 points in free throws.
All together his team scored 50+24+10= 84 points
Mark's opponents scored double his team's number of 2 pointers, meaning they scored 50*2=100 points in 2 pointers.
His opponents scored half his team's number of 3 pointers, meaning they scored 24/2= 12 points in 3 pointers.
They also scored half Mark's team's points in free throws, meaning they scored 10/2=5 points in free throws.
All together Mark's opponents scored 100+12+5=117 points
The total score for the game is both team's scores added together, so it is 84+117=201 points
The answer is 201

Question: Bella has two times as many marbles as frisbees. She also has 20 more frisbees than deck cards. If she buys 2/5 times more of each item, what would be the total number of the items she will have if she currently has 60 marbles?
Let's think step by step
Answer:
When Bella buys 2/5 times more marbles, she'll have increased the number of marbles by 2/5*60 = 24
The total number of marbles she'll have is 60+24 = 84
If Bella currently has 60 marbles, and she has two times as many marbles as frisbees, she has 60/2 = 30 frisbees.
If Bella buys 2/5 times more frisbees, she'll have 2/5*30 = 12 more frisbees.
The total number of frisbees she'll have will increase to 30+12 = 42
Bella also has 20 more frisbees than deck cards, meaning she has 30-20 = 10 deck cards
If she buys 2/5 times more deck cards, she'll have 2/5*10 = 4 more deck cards.
The total number of deck cards she'll have is 10+4 = 14
Together, Bella will have a total of 14+42+84 = 140 items
The answer is 140

Question: A group of 4 fruit baskets contains 9 apples, 15 oranges, and 14 bananas in the first three baskets and 2 less of each fruit in the fourth basket. How many fruits are there?
Let's think step by step
Answer:
For the first three baskets, the number of apples and oranges in one basket is 9+15=24
In total, together with bananas, the number of fruits in one basket is 24+14=38 for the first three baskets.
Since there are three baskets each having 38 fruits, there are 3*38=114 fruits in the first three baskets.
The number of apples in the fourth basket is 9-2=7
There are also 15-2=13 oranges in the fourth basket
The combined number of oranges and apples in the fourth basket is 13+7=20
The fourth basket also contains 14-2=12 bananas.
In total, the fourth basket has 20+12=32 fruits.
The four baskets together have 32+114=146 fruits.
The answer is 146

Question: {}
Let's think step by step. If the question is not sovable, please output [no solution].
Answer:
"""

class CheckAnswerParser:
    def __init__(self, labels) -> None:
        self.labels=labels

    def parse(self, rawtext, example_id):
        answer = gsm8k_postprocess(rawtext)
        label=self.labels[int(example_id)]
        if answer is not None:
            if answer == label:
                return {
                    "solution": rawtext,
                    "answer": answer
                }
            else:
                raise RuntimeError(f"answer is not correct: {answer}, label: {label}")
        else:
            raise RuntimeError("can not parse answer")

class StoreAnswerParser:
    def parse(self, rawtext, example_id):
        if 'no solution' in rawtext.lower():
            raise RuntimeError(f"question is not solvable")

        answer = gsm8k_postprocess(rawtext)
        if answer is not None:
            return rawtext
        else:
            raise RuntimeError("can not parse answer")

class Gsm8kGenerator(BasePipeline):
    @classmethod
    def build_generator(cls, template, parse_func):
        return cls(template, parse_func)

def read_gms8k_data(data_path):
    questions, solutions, answers = [],[],[]
    with open(data_path, 'r') as f:
        for l in f:
            data=json.loads(l)
            question = data['question']
            solution = data['answer']
            final_answer = solution.split('#### ')[1].replace(',', '')
            questions.append(question)
            solutions.append(solution)
            answers.append(final_answer)
    return questions, solutions, answers

if __name__ == '__main__':
    for i in range(4):
        questions, _ = read_gpt_data(f'./generated_data/gms8k_evol_instruct_epoch{i}.jsonl')        

        parser = StoreAnswerParser()
        generator = Gsm8kGenerator.build_generator(template1, parser.parse)

        gpt_outputs = generator.query(
            texts=questions,
            engine='gpt-3.5-turbo', 
            gpt_outputs_path=f'./generated_data/gms8k_evol_solution_epoch{i}.jsonl',
            num_processes=16, 
            retry_limit=5,
            temperature=1.)