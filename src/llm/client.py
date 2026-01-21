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
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content  # 逐段返回给前端
        except Exception as e:
            yield f"生成失败：{str(e)}"

    # ----------------测试岗能力------------

    def parse_requirement_to_testcase(self, requirement_text: str) -> Dict:
        """
        解析需求->生成结构化功能测试用例（json格式），非流式返回
        :param requirement_text: 需求文档
        :return: 生成的测试用例
        """
        prompt = TEST_CASE_PROMPTS.format(requirement_text=requirement_text)
        # # 后端调试，使用非流式返回
        llm_response = self._call_llm_non_stream(prompt)
        return json.loads(llm_response)

    def testcase_to_web_script(self, case_text: str) -> str:
        """
        测试用例->Selenium+pytest标准化脚本，非流式返回
        :param case_text: 测试用例
        :return: 生成的自动化测试脚本
        """
        prompt = WEB_SCRIPT_PROMPTS.format(case_text=case_text)
        script = self._call_llm_non_stream(prompt, force_json=False)
        # # 清理markdown代码块标记
        # script=script.strip("```python").strip("```").strip()
        return script

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
    # from src.paths import *
    # from src.file_utils import FileUtils
    #
    # test = os.path.join(reports_path, "需求文档.docx")
    # test_text = FileUtils.parse_file(test)
    # print(LLMClient().parse_requirement_to_testcase(test_text))
    pass
