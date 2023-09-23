from pipeline import BasePipeline
import json
from utils import math_postprocess, read_math_data, read_gpt_data, is_equiv

template1="""
problem: Let \\[f(x) = \\left\\{{\n\\begin{{array}}{{cl}} ax+3, &\\text{{ if }}x>2, \\\\\nx-5 &\\text{{ if }} -2 \\le x \\le 2, \\\\\n2x-b &\\text{{ if }} x <-2.\n\\end{{array}}\n\\right.\\]Find $a+b$ if the piecewise function is continuous (which means that its graph can be drawn without lifting your pencil from the paper).
solution: For the piecewise function to be continuous, the cases must \"meet\" at $2$ and $-2$. For example, $ax+3$ and $x-5$ must be equal when $x=2$. This implies $a(2)+3=2-5$, which we solve to get $2a=-6 \\Rightarrow a=-3$. Similarly, $x-5$ and $2x-b$ must be equal when $x=-2$. Substituting, we get $-2-5=2(-2)-b$, which implies $b=3$. So $a+b=-3+3=\\boxed{{0}}$.
final answer: 0

problem: If $A=2+i$, $O=-4$, $P=-i$, and $S=2+4i$, find $A-O+P+S$.
solution: Adding real parts and imaginary parts separately, we have $(2-(-4)+0+2)+(1+0-1+4)i=\\boxed{{8+4i}}$.
final answer: 8+4i

problem: {}
Let's step by step to make sure the answer is correct. Your output should be formated as:
solution:
final answer:
If the question is not sovable, please output [no solution].
"""

class CheckAnswerParser:
    def __init__(self, labels) -> None:
        self.labels=labels

    def parse(self, rawtext, example_id):
        answer = math_postprocess(rawtext)
        label=self.labels[int(example_id)]
        if answer is not None:
            if 'finalanswer:' in answer:
                label = 'finalanswer:'+label
            if is_equiv(answer, label):
                return {
                    "solution": rawtext,
                    "answer": answer
                }
            else:
                raise RuntimeError(f"answer is not correct: {answer}, label: {label}")
        else:
            raise RuntimeError("can not parse final answer")

class StoreAnswerParser:
    def parse(self, rawtext, example_id):
        if "no solution" in rawtext.lower():
            raise RuntimeError("no solution")
        return rawtext

class MathGenerator(BasePipeline):
    @classmethod
    def build_generator(cls, template, parse_func):
        return cls(template, parse_func)

if __name__ == '__main__':
    for i in range(4):
        questions, _ = read_gpt_data(f'./generated_data/math_evol_instruct_epoch{i}.jsonl')        

        parser = StoreAnswerParser()
        generator = MathGenerator.build_generator(template1, parser.parse)

        gpt_outputs = generator.query(
            texts=questions,
            engine='gpt-3.5-turbo',
            gpt_outputs_path=f'./generated_data/math_evol_solution_epoch{i}.jsonl',
            num_processes=16, 
            retry_limit=5,
            temperature=1.)