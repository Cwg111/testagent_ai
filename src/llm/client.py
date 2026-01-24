# @FileName  :client.py
# @Time      :2026/1/19 10:11
# @Author    :ChenWenGang
from typing import Dict, Generator
from openai import OpenAI
import json
from src.config import CONFIG
from src.llm.test_case_prompts import TEST_CASE_PROMPTS
from src.llm.web_script_prompts import WEB_SCRIPT_PROMPTS
from src.llm.command_intent_prompts import COMMAND_INTENT_PROMPTS


class LLMClient:
    def __init__(self):
        self.client = OpenAI(api_key=CONFIG["llm"]["api_key"],
                             base_url=CONFIG["llm"]["base_url"],
                             timeout=CONFIG["llm"]["timeout"])
        self.model = CONFIG["llm"]["model"]
        self.temperature = CONFIG["llm"]["temperature"]

    def _build_request_params(self, prompt: str, force_json: bool = True, stream: bool = True) -> Dict:
        """
        抽离公共逻辑：构建LLM请求参数（核心复用部分）
        :param prompt: 提示词
        :param force_json: 是否强制返回JSON格式
        :param stream: 是否流式返回
        :return: 完整的请求参数字典
        """
        request_params = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
        }
        # 可选参数：JSON格式要求
        if force_json:
            request_params["response_format"] = {"type": "json_object"}
        # 流式返回
        if stream:
            request_params["stream"] = True
        return request_params

    def _call_llm_non_stream(self, prompt: str, force_json: bool = True) -> str:
        """
        非流式调用（后端内部解析用，返回字符串）
        """
        # 复用公共参数构建逻辑
        request_params = self._build_request_params(prompt, force_json, stream=False)

        try:
            response = self.client.chat.completions.create(**request_params)
            return response.choices[0].message.content.strip()
        except Exception as e:
            error_msg = f"生成失败：{str(e)}"
            print(error_msg)
            return error_msg

    def _call_llm_stream(self, prompt: str, force_json: bool = True) -> Generator[str, None, None]:
        """
        流式调用（前端实时展示用，返回生成器）
        """
        # 复用公共参数构建逻辑
        request_params = self._build_request_params(prompt, force_json, stream=True)

        try:
            response = self.client.chat.completions.create(**request_params)
            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content  # 逐段返回给前端
        except Exception as e:
            yield f"生成失败：{str(e)}"

    @staticmethod
    def _concat_stream_response(generator: Generator[str, None, None]):
        """
        辅助方法，拼接流式返回的生成器内容为完整字符串
        :param generator: 流式返回的生成器
        :return: 拼接后的完整字符串
        """
        full_content = ""
        for chunk in generator:
            full_content += chunk
        return full_content

    # ----------------测试岗能力------------
    def parse_requirement_to_testcase_stream(self, requirement_text: str) -> Generator[str, None, None]:
        """
        流式返回测试用例JSON（前端实时显示加载过程）
        :param requirement_text: 需求文档
        :return: 生成器
        """
        prompt = TEST_CASE_PROMPTS.format(requirement_text=requirement_text)
        # 逐段返回，前端显示加载过程
        yield from self._call_llm_stream(prompt)

    def parse_requirement_to_testcase(self, requirement_text: str) -> Dict:
        """
        解析需求->生成结构化功能测试用例（json格式）
        :param requirement_text: 需求文档
        :return: 生成的测试用例（字典）
        """
        stream_generator = self.parse_requirement_to_testcase_stream(requirement_text)
        full_json_str = self._concat_stream_response(stream_generator)
        try:
            return json.loads(full_json_str)
        except Exception as e:
            print(f"解析测试用例失败，llm返回非法json：{str(e)}")
            return {}

    def testcase_to_web_script(self, case_text: str) -> Generator[str, None, None]:
        """
        测试用例->Selenium+pytest标准化脚本，流式返回
        :param case_text: 测试用例
        :return: 生成的自动化测试脚本
        """
        prompt = WEB_SCRIPT_PROMPTS.format(case_text=case_text)
        stream_generator = self._call_llm_stream(prompt, force_json=False)
        # 清理markdown代码块标记（流式逐段清理）
        code_block_flag = False
        for chunk in stream_generator:
            # 全局过滤纯"python"的chunk
            if chunk.strip()=="python":
                continue
            if chunk.startswith("```python"):
                code_block_flag = True
                chunk = chunk.replace("```python", "").strip()
            elif chunk.endswith("```"):
                code_block_flag = False
                chunk = chunk.replace("```", "").strip()
            elif code_block_flag:
                pass  # 中间块直接返回
            yield chunk

    def parse_command_intent(self, command_text: str) -> Dict:
        """
        解析用户指令意图（兜底用，关键字匹配失败时调用），非流式返回
        :param command_text: 指令
        :return: 解析结果
        """
        prompt = COMMAND_INTENT_PROMPTS.format(command_text=command_text)
        llm_response = self._call_llm_non_stream(prompt)
        return json.loads(llm_response)


if __name__ == "__main__":
    # # ---测试基于需求文档生成测试用例---
    # from src.paths import *
    # from src.file_utils import FileUtils
    #
    # test = os.path.join(test_file_path, "需求文档.docx")
    # test_text = FileUtils.parse_file(test)
    # client = LLMClient()
    # # 使用流式方法，逐段输出
    # print("开始生成测试用例...")
    # print("=" * 50)
    # full_response = ""
    # for chunk in client.parse_requirement_to_testcase_stream(test_text):
    #     print(chunk, end="", flush=True)
    #     full_response += chunk

    # # ---测试基于测试用例生成Selenium+pytest脚本---
    # from src.paths import *
    # from src.file_utils import FileUtils
    #
    # test = os.path.join(test_file_path, "电商系统V2.0测试用例.xlsx")
    # test_text = FileUtils.parse_file(test)
    # client = LLMClient()
    # # 使用流式方法，逐段输出
    # print("开始生成web自动化测试脚本...")
    # print("=" * 50)
    # full_response = ""
    # for chunk in client.testcase_to_web_script(test_text):
    #     print(chunk, end="", flush=True)
    #     full_response += chunk

    # # ---测试解析用户指令意图---
    # print(LLMClient().parse_command_intent("你怎么就直接从需求文档生成测试脚本了，我没这么设计啊"))
    pass
