# Toolkit for chatgpt api
1. apikeys保存在apikeys.py中，可以通过`python apikeys.py`测试key的有效性，如果失效了 需要更新key

2. api_utils.py提供了两个调用api的接口：
- `query_chatgpt_and_save_results`: 调用api，并保存gpt的结果，通过设置reuse_existing_outputs可以复用之前已经生成的结果，否则会覆盖之前生成的结果（这个设计是因为生成可能会因为一些意外中断）
- `query_chatgpt`: 调用api并用传入的post_function处理gpt的生成结果

3. pipeline.py提供了方便的接口去根据特定的任务定义pipeline，只需要在构建pipeline的时候传入template和parse function：
```python
from pipeline import BasePipeline

template = "xxx"
def parse_func():
    ...

class CustomPipeline(BasePipeline):
    @classmethod
    def build():
        return cls(template, parse_func)

pipeline = CustomPipeline.build()

# 设置gpt_outputs_path可以将output写入文件，每次调用api前会读取已经写入文件的结果。如果数据量大，或者调用api不稳定，设置gpt_outputs_path会很有帮助
query(
    texts=texts,
    engine='gpt-3.5-turbo', 
    gpt_outputs_path=None,
    num_processes=10, 
    retry_limit=5,
    temperature=0.)
```

4. examples提供了1个调用api的项目：
- pretrain_data_filter: 过滤、改写低质量语料