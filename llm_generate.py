# -*- coding: utf -8 -*- #
"""
@filename:llm_generate.py
@author:ChenWenGang
@time:2026-01-09
"""
import openai
from config_loader import CONFIG


# 初始化大模型客户端
def init_llm_client():
    client = openai.OpenAI(
        api_key=CONFIG["llm"]["api_key"],
        base_url=CONFIG["llm"]["base_url"],
    )
    return client


def generate_script(prompt):
    client = init_llm_client()
    try:
        response = client.chat.completions.create(
            model=CONFIG["llm"]["model"],
            messages=[{"role": "user", "content": prompt}],
            temperature=CONFIG["llm"]["temperature"]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"生成失败，{str(e)}"


if __name__ == '__main__':
    test_prompt = "生成一个简单的Python+Requests接口测试脚本，请求GET https://httpbin.org/get，断言状态码为200"
    print(generate_script(test_prompt))
