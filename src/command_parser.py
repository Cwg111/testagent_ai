# @FileName  :command_parser.py
# @Time      :2026/1/20 17:13
# @Author    :ChenWenGang
# ---解析用户输入的内容----
from src.llm.client import LLMClient
from typing import Dict


class CommandParser:
    def __init__(self):
        self.llm_client = LLMClient()

    def parse_command(self, command_text: str) -> Dict:
        """
        解析用户指令，返回结构化意图
        :param command_text: 用户输入的自然语言指令
        :return: {"intent":str,"use_context":bool}
        intent指的是generate_case"|"generate_web_script"|"generate_api_script"|"generate_requirements_checklist"
        |"general"；
        use_context指的是是否使用上下文
        """
        command = command_text.strip()
        if not command:
            return {"intent": None, "use_context": False}
        intent = None
        use_context = False

        # LLM识别用户指令意图
        try:
            llm_result = self.llm_client.parse_command_intent(command)
        except Exception as e:
            print(f"LLM解析失败，请检查输入指令：{e}")
        else:
            intent = llm_result["intent"]
            use_context = llm_result["use_context"]

        return {"intent": intent,
                "use_context": use_context
                }


if __name__ == "__main__":
    print(CommandParser().parse_command("测试一下trae的git提交"))
    run_code = 0
