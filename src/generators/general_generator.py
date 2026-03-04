# -*- coding: utf -8 -*- #
"""
@filename:general_generator.py
@author:ChenWenGang
@time:2026-01-25
"""
import datetime
from typing import Dict, Generator
from src.llm.client import LLMClient
from src.file_utils import FileUtils
from src.paths import *


class GeneralGenerator:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def handle_general(self, command_text: str,use_context: bool, file_path: str , session_id: str ) -> Generator[
        Dict, None, None]:
        """
        流式生成通用大模型回答的内容
        :param command_text: 通用大模型需要用户输入的原文
        :param file_path: 上传的测试用例文件路径，当需要上下文时可以不用上传文件
        :param use_context: 是否需要上下文
        :param session_id: 会话ID
        :yield: 流式返回字典，格式：
        {
            "type":"status"/"content"/"final"/"error"
            "session_id":str,
            "data":状态信息/实时内容/最终结果/错误信息
        }
        """
        # 如果用户输入的指令中包含上下文，则返回提示信息
        if use_context:
            yield {
                "type": "status",
                "session_id": session_id,
                "data": "抱歉，通用大模型暂不支持上下文，敬请期待"
            }
        if file_path:
            # 返回状态，开始解析用例
            yield {
                "type": "status",
                "session_id": session_id,
                "data": "开始解析您上传的文档，并回答您的问题..."
            }
            # 解析用户上传的文档
            file_text = FileUtils.parse_file(file_path)
            answer_stream = self.llm_client.general_stream(command_text, file_text)
        else:
            yield {
                "type": "status",
                "session_id": session_id,
                "data": "开始回答您问题..."
            }
            answer_stream = self.llm_client.general_stream(command_text)
        full_answer = ""
        for chunk in answer_stream:
            full_answer += chunk
            yield {
                "type": "success",
                "session_id": session_id,
                "data": chunk  # 前端实时显示输出的内容
            }

        # 保存输出的内容
        answer_filename = f"general_answer_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        save_answer_path = os.path.join(general_answers_path, answer_filename)
        with open(save_answer_path, "w", encoding="utf-8") as f:
            f.write(full_answer)

        # 返回最终结果
        yield {
            "type": "final",
            "session_id": session_id,
            "data": {
                "status": "success",
                "message": "已成功回答您的问题",
                "file_path": save_answer_path,
                "script_content": full_answer
            }
        }


if __name__ == '__main__':
    pass
