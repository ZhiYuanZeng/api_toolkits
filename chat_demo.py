# -*- coding:utf-8 -*-

# @Author:      zp
# @Time:        2023/4/7 15:19

import openai

openai.api_base = "https://ai-proxy.shlab.tech/internal"
# 输入完整token
openai.api_key = "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"


def chat(message: str, model="gpt-3.5-turbo") -> str:
    """
    model: gpt-3.5-turbo, gpt-3.5-turbo-0301, gpt-4
    """
    message_log = [{"role": "user", "content": message}]
    completion = openai.ChatCompletion.create(model=model,
                                              messages=message_log)
    res = completion.choices[0].message.content

    print(f"question: {message} ===> answer: {res}")
    return res



if __name__ == "__main__":
    datas = ["俄"*5000]
    for one_qa in datas:
        ress = chat(one_qa)
