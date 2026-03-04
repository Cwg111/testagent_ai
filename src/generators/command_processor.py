# -*- coding: utf -8 -*- #
"""
@filename:command_processor.py
@author:ChenWenGang
@time:2026-01-25
"""
from typing import Dict,Generator
from src.generators.case_web_generator import TestGenerator
from src.generators.dev_generator import DevGenerator
from src.generators.product_generator import ProductGenerator
from src.generators.general_generator import GeneralGenerator
from src.command_parser import CommandParser
from src.context_manager import session_manager
from src.llm.client import LLMClient
import traceback

class CommandDispatcher:
    """
    指令调度，统一处理指令，根据指令调度不同的生成器
    """
    def __init__(self):
        self.llm_client=LLMClient()
        self.case_web_generator=TestGenerator(llm_client=self.llm_client)
        self.api_generator=DevGenerator(llm_client=self.llm_client)
        self.checklist_generator=ProductGenerator(llm_client=self.llm_client)
        self.general_generator=GeneralGenerator(llm_client=self.llm_client)
        self.command_parser=CommandParser()

    def process_by_command(self, file_path: str, command_text: str, session_id: str ) -> Generator[
        Dict, None, None]:
        """
        根据不同的指令调用不同的生成器函数
        :param file_path: 需求文档/用例文件/接口文档路径
        :param command_text: 用户输入的自然语言指令
        :param session_id: 当前会话ID，默认为None
        :yield: 流式返回字典，格式：
        {
            "type":"status"/"content"/"final"/"error"
            "session_id":str,
            "data":状态信息/实时内容/最终结果/错误信息
        }
        """
        if not command_text or command_text.strip() == "":
            # 即使前端校验了，后端也要拦截
            yield {
                "type": "error",
                "session_id": session_id,  # 此时session_id可能为None，不影响错误提示
                "data": "指令内容不能为空，请输入有效的需求指令"
            }
            return

        session = session_manager.get_session(session_id)
        current_session_id = session.session_id
        yield {
            "type": "status",
            "session_id": current_session_id,
            "data": "开始处理指令"
        }

        try:
            command_intent = self.command_parser.parse_command(command_text)
            intent = command_intent["intent"]
            use_context = command_intent["use_context"]
            if intent == "generate_case":
                yield from self.case_web_generator.handle_generate_case(file_path, current_session_id)
            elif intent == "generate_web_script":
                yield from self.case_web_generator.handle_generate_web_script(use_context, file_path, current_session_id)
            elif intent == "generate_api_script":
                yield from self.api_generator.handle_generate_api_script(file_path, current_session_id)
            elif intent == "generate_requirements_checklist":
                yield from self.checklist_generator.handle_generate_checklist(file_path, current_session_id)
            else:
                yield from self.general_generator.handle_general(command_text, use_context, file_path, current_session_id)
        except Exception as e:
            error_detail = f"生成失败：\n错误类型：{type(e).__name__}\n错误内容：{str(e)}\n堆栈信息：\n{traceback.format_exc()}"
            yield {
                "type": "error",
                "session_id": current_session_id,
                # "data": f"生成失败：{str(e)}"
                "data":error_detail
            }
            return
if __name__ == '__main__':
    # from src.paths import *
    # file_path=os.path.join(test_file_path, "电商系统V2.0需求文档.docx")
    # dispatcher=CommandDispatcher()
    # for chunk in dispatcher.process_by_command(file_path, "帮我阅读一下这个文档，总结一下"):
    #     print(chunk)
    pass
