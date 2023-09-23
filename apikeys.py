import openai
openai.api_base = "https://ai-proxy.shlab.tech/internal"

# 如果key失效，找徐瑞良
APIKEYS=[
    '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'

]
GPT4_APIKEYS=[
    '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',
    #'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'

]

PERSPECTIVE_APIKEYS = [
    'AIzaSyCK9teFVz_GYSxrsVYnJX42-HFEYDPpeJE'
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
