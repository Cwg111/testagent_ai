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
        command = command_text.strip()
        if not command:
            return {"intent": None, "use_context": False, "confidence": 0.0}
        intent=None
        use_context=False

        # 匹配“生成测试用例”意图
        for kw in self.CASE_INTENT_KEYWORDS:
            if kw in command:
                intent = "generate_case"
                break

        # 匹配“生成测试脚本”意图
        if not intent:
            for kw in self.SCRIPT_INTENT_KEYWORDS:
                if kw in command:
                    intent = "generate_script"
                    # 检查是否需要上下文
                    for ctx_kw in self.CONTEXT_KEYWORDS:
                        if ctx_kw in command:
                            use_context = True
                            break
                    break

        # LLM兜底（关键字匹配失败时）
        if not intent:
            try:
                llm_result=self.llm_client.parse_command_intent(command)
            except Exception as e:
                print(f"LLM解析失败，请检查输入指令：{e}")
            else:
                intent = llm_result["intent"]
                use_context = llm_result["use_context"]
        return {"intent": intent,
                "use_context": use_context,
                "confidence": 1.0 if intent else 0.0}


if __name__ == "__main__":
    run_code = 0
