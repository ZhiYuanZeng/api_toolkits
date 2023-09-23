import openai
import json
from api_utils import query_chatgpt_and_save_results
from apikeys import APIKEYS
import argparse
import os


class Template:
    template1="Determine the educational value of the following code for a student to learn basic coding concepts:\n\
    you should answer wether the educational value of these code is high or low. \n\
    Note that if you should answer high, the code would be useful for student to follow and learn basic coding concepts. \n\
    If it is difficult for you to determine that, please answer low.\n\
    The educational value of these code is {}"

    template2="""
    Assume you are a student who understands lots of theoretical knowledge but lacks programming experience. You found the following codes from the internet:
    ```
    {}
    ```
    For a student who have strong theoretical knowledge but lacks programming experience, do you think these codes are helpful? Answer [yes] or [no], if you are not sure just answer [no]
    """

    template3="""
    ```
    {}
    ```
    For a student who have strong theoretical knowledge but lacks programming experience, do you think these codes are helpful? Answer [yes] or [no].
    If you can not determine, please answer [Not sure]
    """

    template4="""
    For a student who have strong theoretical knowledge but lacks programming experience, do you think the following codes are educational and helpful? Can they appear in a textbook or tutorial?Answer [yes]/[no]/[not sure]. If the answer is [yes], what kinds of textbook can these codes appear?
    [Code]:
    ```
    {}
    ```
    [Output]: yes, the code may be in a textbook about machine learning 

    [Code]:
    ```
    {}
    ```
    [Output]: no

    [Code]
    ```
    {}
    ```
    [Output]:
    """

    template5="""
    Are the following code examples suitable for students who possess strong theoretical knowledge but lack programming experience? Educational codes should meet the following criteria: clarity, self-containment, instructiveness, modularity, and reusability.

    Clarity: The codes should have a clear purpose and functionality, with meaningful variable and function names.

    Self-containment: The codes should include all necessary components. Imported packages should be public and well-known.

    Modularity and Reusability: The codes should be structured into smaller, reusable functions or classes.

    Please answer with either [yes], [no], or [not sure]. If the answer is [yes], please use at most 30 words to describe what do the codes do.

    [Code]:
    ```
    {}
    ```
    [Output]: yes. The code defines a Student class with attributes for name, age, and grades. It provides methods to add grades and calculate the average grade for a student, demonstrating usage with an example.

    [Code]:
    ```
    {}
    ```
    [Output]: no

    [Code]
    ```
    {}
    ```
    [Output]:
    """

openai.api_base = "https://ai-proxy.shlab.tech/internal"
parser = argparse.ArgumentParser(description='Description of your script')
parser.add_argument('--input_dir', help='Help message for arg_name')
parser.add_argument('--output_dir', help='Help message for arg_name')

with open('good_example.py', 'r') as f:
    good_example=f.read()
with open('bad_example.py', 'r') as f:
    bad_example=f.read()

args = parser.parse_args()

all_input_paths = []
all_output_paths = []
for file in os.listdir(args.input_dir, ):
    all_input_paths.append(os.path.join(args.input_dir, file))
    all_output_paths.append(os.path.join(args.output_dir, file))

for ipath, opath in zip(all_input_paths, all_output_paths):
    instances = []
    with open(ipath) as f:
        for i,l in enumerate(f):
            query=json.loads(l)
            query=Template.template5.format(good_example, bad_example, query['content'])
            instance={
                "prompt": query,
                "id":i
            }
            instances.append(instance)

    query_chatgpt_and_save_results(apikeys=APIKEYS, engine='gpt-3.5-turbo', instances=instances, output_path=opath, max_tokens=100, num_processes=16)
