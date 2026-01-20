# @FileName  :command_parser.py
# @Time      :2026/1/20 17:13
# @Author    :ChenWenGang
# ---解析用户输入的内容----
from src.llm.client import LLMClient
from typing import Dict


class CommandParser:
    def __init__(self):
        self.llm_client = LLMClient()
        # 核心关键词库（中文指令匹配）
        self.CASE_INTENT_KEYWORDS = [
            "生成测试用例",
            "创建用例",
            "编写测试用例",
        ]
        self.SCRIPT_INTENT_KEYWORDS = [
            "生成脚本",
            "创建测试脚本",
            "编写测试脚本",
            "生成自动化测试脚本",
        ]
        self.CONTEXT_KEYWORDS = [
            "上面",
            "之前",
            "已生成的",
        ]

    def parse_command(self, command_text: str) -> Dict:
        """
        解析用户指令，返回结构化意图
        :param command_text: 用户输入的自然语言指令
        :return: {"intent":str,"use_context":bool,"confidence":float}
        intent指的是是生成用例，还是生成代码；
        use_context指的是是否使用上下文
        confidence指的是程序对“解析出来的用户意图是否准确”的把握程度
        """
        pass


if __name__ == "__main__":
    run_code = 0
