# @FileName  :dev_generator.py
# @Time      :2026/1/19 10:13
# @Author    :ChenWenGang
import datetime
from typing import Dict, Generator
from src.llm.client import LLMClient
from src.file_utils import FileUtils
from src.paths import *


class DevGenerator:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def handle_generate_api_script(self, file_path: str , session_id: str ) -> Generator[
        Dict, None, None]:
        """
        流式生成生成requests+python接口自动化测试脚本
        :param file_path: 上传的接口文档文件路径
        :param session_id: 会话ID
        :yield: 流式返回字典，格式：
        {
            "type":"status"/"content"/"final"/"error"
            "session_id":str,
            "data":状态信息/实时内容/最终结果/错误信息
        }
        """

        if not file_path:
            yield {
                "type": "error",
                "session_id": session_id,
                "data": "生成接口自动化脚本需要上传接口文档"
            }
            return  # 当解析失败时，返回错误信息，不再执行后续代码

        # 返回状态，开始解析接口文档
        yield {
            "type": "status",
            "session_id": session_id,
            "data": "开始解析接口文档，生成接口自动化测试脚本中..."
        }

        # 解析接口文档，生成requests+python脚本
        api_text = FileUtils.parse_file(file_path)
        script_stream = self.llm_client.api_to_script(api_text)
        full_script = ""
        for chunk in script_stream:
            full_script += chunk
            yield {
                "type": "success",
                "session_id": session_id,
                "data": chunk  # 前端实时显示脚本片段
            }

        # 保存脚本文件
        script_filename = f"test_api_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.py"
        save_script_path = os.path.join(api_script_path, script_filename)
        with open(save_script_path, "w", encoding="utf-8") as f:
            f.write(full_script)

        # 返回最终结果
        yield {
            "type": "final",
            "session_id": session_id,
            "data": {
                "status": "success",
                "message": "生成接口自动化测试脚本成功",
                "file_path": save_script_path,
                "script_content": full_script
            }
        }


if __name__ == "__main__":
    run_code = 0
