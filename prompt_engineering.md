# Prompt Engineering
1. 用GPT4可以很容易找到一个初始的 不错的prompt
2. 打分的prompt：
    - 可以细化评价指标，在指标上打分后，再打一个overall score，甚至可以在gpt score的基础上训练一个classifier
    - 打分的边界会对结果产生一些影响，例如1~5, 1~10
    - 可以设置temperature=0. (greedy)，因为不需要diversity
    - 在playground上测试，一次只能测单个样例，不然测出的结果和调用api的结果不一样 (in-context learning)
    - 随机sample chatgpt分类错误的样本作为in-context learning的样例可能会有用 (还没有测试过，因为数据量少)
3. 生成的prompt:
    - temperature应该设置成>=1
    - 如果是条件生成，例如改写，翻译，不需要做多少prompt调整
    - 如果是开放式生成，例如self-instruct，需要控制diversity，控制diversity有3个方法：
        1. 调整temperature，增加temperature也会增加噪声
        2. 提高seed example的diversity
        3. 让模型每次多生成一些数据，用10次api调用，每次生成10个样本和用1次api调用，每次生成100个样本，后者的diversity会高很多。但是因为模型的context window是有限的，所以可以采用层次化的生成策略，例如先生成标题，主题，关键字再生成文本。生成标题一次性生成100个，生成内容时每次根据给定的10个标题生成10个完整的样本。
4. parsing: 从chatgpt的生成结果解析出想要的答案
    - prompt里面通常需要指定答案的format，甚至需要给出example，但是chatgpt不一定会follow提示
    - temperature=0时，生成结果通常会follow指定的format，但是随着temperature的增加 解析错误的样本数量会增多
    - 不要去指定json, xml等格式，如果答案简单，很容易就能解析出来，如果答案复杂，json，xml很难work