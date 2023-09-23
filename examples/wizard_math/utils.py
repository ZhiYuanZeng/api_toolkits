import os
import json
import re

def last_boxed_only_string(string):
    idx = string.rfind("\\boxed")
    if idx < 0:
        idx = string.rfind("\\fbox")
        if idx < 0:
            return None

    i = idx
    right_brace_idx = None
    num_left_braces_open = 0
    while i < len(string):
        if string[i] == "{":
            num_left_braces_open += 1
        if string[i] == "}":
            num_left_braces_open -= 1
            if num_left_braces_open == 0:
                right_brace_idx = i
                break
        i += 1
    
    if right_brace_idx == None:
        retval = None
    else:
        retval = string[idx:right_brace_idx + 1]
    
    return retval

def remove_boxed(s):
    left = "\\boxed{"
    try:
        assert s[:len(left)] == left
        assert s[-1] == "}"
        return s[len(left):-1]
    except:
        return None

def _fix_fracs(string):
    substrs = string.split("\\frac")
    new_str = substrs[0]
    if len(substrs) > 1:
        substrs = substrs[1:]
        for substr in substrs:
            new_str += "\\frac"
            if substr[0] == "{":
                new_str += substr
            else:
                try:
                    assert len(substr) >= 2
                except:
                    return string
                a = substr[0]
                b = substr[1]
                if b != "{":
                    if len(substr) > 2:
                        post_substr = substr[2:]
                        new_str += "{" + a + "}{" + b + "}" + post_substr
                    else:
                        new_str += "{" + a + "}{" + b + "}"
                else:
                    if len(substr) > 2:
                        post_substr = substr[2:]
                        new_str += "{" + a + "}" + b + post_substr
                    else:
                        new_str += "{" + a + "}" + b
    string = new_str
    return string

def _fix_a_slash_b(string):
    if len(string.split("/")) != 2:
        return string
    a = string.split("/")[0]
    b = string.split("/")[1]
    try:
        a = int(a)
        b = int(b)
        assert string == "{}/{}".format(a, b)
        new_string = "\\frac{" + str(a) + "}{" + str(b) + "}"
        return new_string
    except:
        return string

def _remove_right_units(string):
    # "\\text{ " only ever occurs (at least in the val set) when describing units
    if "\\text{ " in string:
        splits = string.split("\\text{ ")
        assert len(splits) == 2
        return splits[0]
    else:
        return string

def _fix_sqrt(string):
    if "\\sqrt" not in string:
        return string
    splits = string.split("\\sqrt")
    new_string = splits[0] 
    for split in splits[1:]:
        if split[0] != "{":
            a = split[0]
            new_substr = "\\sqrt{" + a + "}" + split[1:]
        else:
            new_substr = "\\sqrt" + split
        new_string += new_substr
    return new_string

def _strip_string(string):
    string = string.replace('\pi', 'π')
    string = string.replace(',', "")
    string = string.replace('-\infty', "-\iny")
    # linebreaks  
    string = string.replace("\n", "")
    #print(string)

    # remove inverse spaces
    string = string.replace("\\!", "")
    #print(string)

    # replace \\ with \
    string = string.replace("\\\\", "\\")
    #print(string)

    # replace tfrac and dfrac with frac
    string = string.replace("tfrac", "frac")
    string = string.replace("dfrac", "frac")
    #print(string)

    # remove \left and \right
    string = string.replace("\\left", "")
    string = string.replace("\\right", "")
    #print(string)
    
    # Remove circ (degrees)
    string = string.replace("^{\\circ}", "")
    string = string.replace("^\\circ", "")

    # remove dollar signs
    string = string.replace("\\$", "")
    
    # remove units (on the right)
    string = _remove_right_units(string)

    # remove percentage
    string = string.replace("\\%", "")
    string = string.replace("\%", "")
    string = string.replace("%", "")

    # " 0." equivalent to " ." and "{0." equivalent to "{." Alternatively, add "0" if "." is the start of the string
    string = string.replace(" .", " 0.")
    string = string.replace("{.", "{0.")
    # if empty, return empty string
    if len(string) == 0:
        return string
    if string[0] == ".":
        string = "0" + string

    # to consider: get rid of e.g. "k = " or "q = " at beginning
    if len(string.split("=")) == 2:
        if len(string.split("=")[0]) <= 2:
            string = string.split("=")[1]

    # fix sqrt3 --> sqrt{3}
    string = _fix_sqrt(string)

    # remove spaces
    string = string.replace(" ", "")

    # \frac1b or \frac12 --> \frac{1}{b} and \frac{1}{2}, etc. Even works with \frac1{72} (but not \frac{72}1). Also does a/b --> \\frac{a}{b}
    string = _fix_fracs(string)

    # manually change 0.5 --> \frac{1}{2}
    if string == "0.5":
        string = "\\frac{1}{2}"

    # NOTE: X/Y changed to \frac{X}{Y} in dataset, but in simple cases fix in case the model output is X/Y
    string = _fix_a_slash_b(string)

    return string

def is_equiv(str1, str2, verbose=False):
    if str1 is None and str2 is None:
        print("WARNING: Both None")
        return True
    if str1 is None or str2 is None:
        return False

    try:
        ss1 = _strip_string(str1)
        ss2 = _strip_string(str2)
        if verbose:
            print(ss1, ss2)
        return ss1 == ss2
    except:
        return str1 == str2
    
def math_postprocess(text: str) -> str:
    SUBSTITUTIONS = [('an ', ''), ('a ', ''), ('.$', '$'), ('\\$', ''),
                     (r'\ ', ''), (' ', ''), ('mbox', 'text'),
                     (',\\text{and}', ','), ('\\text{and}', ','),
                     ('\\text{m}', '\\text{}'), ('\\le', '<')]
    REMOVED_EXPRESSIONS = [
        'square', 'ways', 'integers', 'dollars', 'mph', 'inches', 'ft',
        'hours', 'km', 'units', '\\ldots', 'sue', 'points', 'feet', 'minutes',
        'digits', 'cents', 'degrees', 'cm', 'gm', 'pounds', 'meters', 'meals',
        'edges', 'students', 'childrentickets', 'multiples', 'miles', 'point', '2kPa', '\\text{s}',
        '\\text{.}', '\\text{\ns}', '\\text{}^2', '\\text{}^3', '\\text{\n}',
        '\\text{}', r'\mathrm{th}', r'^\circ', r'^{\circ}', r'\;', r',\!',
        '{,}', '"', '\\dots', '\n', '\r', '\f'
    ]

    def normalize_final_answer(final_answer: str) -> str:
        """Normalize a final answer to a quantitative reasoning question."""
        # final_answer = final_answer.split('=')[-1]
        for before, after in SUBSTITUTIONS:
            final_answer = final_answer.replace(before, after)
        for expr in REMOVED_EXPRESSIONS:
            final_answer = final_answer.replace(expr, '')

        # Extract answer that is in LaTeX math, is bold,
        # is surrounded by a box, etc.
        final_answer = re.sub(r'(\\text\{)(.*?)(\})', '\\2', final_answer)
        final_answer = re.sub(r'(\\textbf\{)(.*?)(\})', '\\2', final_answer)
        final_answer = re.sub(r'(\\overline\{)(.*?)(\})', '\\2', final_answer)
        final_answer = re.sub(r'(\\boxed\{)(.*)(\})', '\\2', final_answer)
        assert '\n' not in final_answer
        assert '\r' not in final_answer
        assert '\f' not in final_answer
        if len(re.findall(r'finalansweris(.*)', final_answer)) > 0:
            final_answer = re.findall(r'finalansweris(.*)', final_answer)[-1]

        if len(re.findall(r'oxed\{(.*?)\}', final_answer)) > 0:
            final_answer = re.findall(r'oxed\{(.*?)\}', final_answer)[-1]

        if len(re.findall(r'\$(.*?)\$', final_answer)) > 0:
            final_answer = re.findall(r'\$(.*?)\$', final_answer)[-1]
        final_answer = final_answer.strip()
        if 'rac' in final_answer and '\\frac' not in final_answer:
            final_answer = final_answer.replace('rac', '\\frac')

        # Normalize shorthand TeX:
        # \fracab -> \frac{a}{b}
        # \frac{abc}{bef} -> \frac{abc}{bef}
        # \fracabc -> \frac{a}{b}c
        # \sqrta -> \sqrt{a}
        # \sqrtab -> sqrt{a}b
        final_answer = re.sub(r'(frac)([^{])(.)', 'frac{\\2}{\\3}',
                              final_answer)
        final_answer = re.sub(r'(sqrt)([^{])', 'sqrt{\\2}', final_answer)
        final_answer = final_answer.replace('$', '')

        # Normalize 100,000 -> 100000
        if final_answer.replace(',', '').isdigit():
            final_answer = final_answer.replace(',', '')
        
        if '=' in final_answer:
            final_answer = final_answer.split('=')[-1]
        return final_answer
    
    all_maybe_answers = []
    for maybe_ans in text.split('\n'):
        for _mayebe_ans in maybe_ans.split('. '):
            all_maybe_answers.append(_mayebe_ans)
    all_maybe_answers = reversed(all_maybe_answers) # iterate from the last sentence

    for a in all_maybe_answers:
        if 'final answer' in a.lower():
            return normalize_final_answer(a)
    
    for a in all_maybe_answers:
        if a.strip() != '':
            return normalize_final_answer(a)
        
def gsm8k_postprocess(text: str) -> str:
    # regex pattern to match all numbers in the text
    pattern = r'\b\d+\b'

    # find all occurrences of the pattern in the text
    numbers = re.findall(pattern, text)

    # get the last number
    last_number = numbers[-1]

    return last_number

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

def read_math_data(data_dir):
    questions = []
    solutions = []
    answers = []
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if not file.endswith('.json'):
                continue
            path=os.path.join(root, file)
            with open(path, 'r') as f:
                data=json.load(f)
                try:
                    answer = remove_boxed(last_boxed_only_string(data['solution']))
                    questions.append(data['problem'])
                    solutions.append(data['solution'])
                    answers.append(answer)
                except Exception:
                    print('parsing error:' + data['solution']) 
    return questions, solutions, answers

def read_gpt_data(data_path):
    questions = []
    ids = []
    with open(data_path, 'r') as f:
        for l in f:
            data=json.loads(l)
            questions.append(data['output'])
            ids.append(int(data['id']))
    return questions, ids