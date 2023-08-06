import openai
openai.api_base = "https://ai-proxy.shlab.tech/internal"

APIKEYS=[
    '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',
    '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',
    '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',
    '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'
]
GPT4_APIKEYS=[
    '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'
]


def _check_key(message: str, key='', model='gpt-3.5-turbo') -> str:
    """
    model: gpt-3.5-turbo, gpt-3.5-turbo-0301, gpt-4
    """
    model="gpt-3.5-turbo"
    message_log = [{"role": "user", "content": message}]
    openai.api_key = key

    completion = openai.ChatCompletion.create(model=model,
                                              messages=message_log,
                                              max_tokens=1)
    res = completion.choices[0].message.content

    print(f"key:{key}, question: {message} ===> answer: {res}")
    return res


if __name__=='__main__':
    for key in APIKEYS:
        datas = 'hello'
        _check_key(datas, key)
    print('gpt3.5 keys are fine')
    
    for key in GPT4_APIKEYS:
        datas = 'hello'
        _check_key(datas, key, model='gpt-4')
    print('gpt4 keys are fine')
