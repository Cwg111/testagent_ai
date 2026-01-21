# @FileName  :test_generator.py
# @Time      :2026/1/19 10:12
# @Author    :ChenWenGang
import datetime
import json
from typing import Dict
from src.llm.client import LLMClient
from src.command_parser import CommandParser
from src.context_manager import session_manager
from src.file_utils import FileUtils
from src.paths import *


class TestGenerator:
    def __init__(self):
        self.llm_client = LLMClient()
        self.command_parser = CommandParser()

    def process_by_command(self, file_path: str, command_text: str, session_id: str = None) -> Dict:
        """
        核心入口，生成测试用例/测试脚本
        :param file_path: 需求文档路径
        :param command_text: 用户输入的自然语言指令
        :param session_id: 当前会话ID，默认为None
        :return: 智能体生成的内容及一些状态信息
        """
        session = session_manager.get_session(session_id)
        current_session_id = session.session_id

        try:
            command_intent = self.command_parser.parse_command(command_text)
            intent = command_intent["intent"]
            use_context = command_intent["use_context"]
            if intent == "generate_case":
                return self._handle_generate_case(file_path, current_session_id)
            elif intent == "generate_script":
                return self._handle_generate_script(file_path, current_session_id)
            else:
                return {
                    "status": "error",
                    "message": f"无法识别指令：{command_text}，请重新输入",
                    "session_id": current_session_id
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"生成失败，{str(e)}",
                "session_id": current_session_id
            }

    def _handle_generate_case(self, file_path: str, session_id: str = None) -> Dict:
        """
        生成测试用例（返回表格渲染数据）
        :param file_path: 需求文档路径
        :param session_id: 当前会话的ID
        :return: 智能体生成的内容以及相关信息
        """
        if not file_path:
            return {
                "status": "error",
                "message": "生成测试用例需要上传需求文档",
                "session_id": session_id
            }
        requirement_text = FileUtils.parse_file(file_path)
        case_data = self.llm_client.parse_requirement_to_testcase(requirement_text)
        # 保存用例JSON文件
        test_suite = case_data.get("test_suite", "未知套件")
        case_filename = f"{test_suite}_case_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.json"
        save_case_path = os.path.join(case_path, case_filename)
        with open(save_case_path, "w", encoding="utf-8") as f:
            json.dump(case_data, f, indent=2, ensure_ascii=False)
        # 本次会话记住生成的用例路径，下次请求时使用
        session_manager.save_case_path(session_id, save_case_path)
        return {
            "status": "success",
            "message": "生成成功",
            "file_path": save_case_path,
            "data": self._convert_to_table_format(case_data),
            "session_id": session_id
        }

    def _handle_generate_script(self, file_path: str, use_context: bool, session_id: str = None) -> Dict:
        """
        生成Selenium+pytest测试脚本
        :param file_path: 上传的测试用例文件路径
        :param use_context: 是否需要上下文
        :param session_id: 会话ID
        :return: 返回生成的脚本
        """
        # 确定用例路径
        case_path = ""
        if use_context:
            case_path = session_manager.get_case_path(session_id)
            if not case_path:
                return {
                    "status": "error",
                    "message": "本次会话未生成测试用例，请先上传需求文档",
                    "session_id": session_id
                }
        else:
            if not file_path:
                return {
                    "status": "error",
                    "message": "生成测试脚本需要上传测试用例文件",
                    "session_id": session_id
                }
            case_path = file_path

        # 解析用例，生成Selenium+pytest脚本
        case_text = FileUtils.parse_file(case_path)
        script_code = self.llm_client.testcase_to_web_script(case_text)

        # 保存脚本文件
        script_filename = f"test_web_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.py"
        save_script_path = os.path.join(web_script_path, script_filename)
        with open(save_script_path, "w", encoding="utf-8") as f:
            f.write(script_code)

        return {
            "status": "success",
            "message": "Selenium+pytest脚本生成成功",
            "file_path": save_script_path,
            "session_id": session_id
        }

    @staticmethod
    def _convert_to_table_format(case_data: Dict) -> list:
        """
        将大模型返回的测试用例数据转换为前端表格格式
        :param case_data: 大模型返回的测试用例数据
        :return: 表格格式的测试用例数据
        """
        table_data = []

        # 获取所有模块
        modules = case_data.get('modules', [])

        for module in modules:
            feature = module.get('feature', '未知模块')
            module_desc = module.get('module_desc', '')
            cases = module.get('cases', [])

            # 遍历模块下的所有测试用例
            for case in cases:
                # 将步骤列表转换为字符串（用换行符连接）
                steps_str = '\n'.join(case.get('steps', []))

                # 构建表格行数据
                table_row = {
                    'feature': feature,  # 功能模块
                    'module_desc': module_desc,  # 模块描述
                    'case_id': case.get('case_id', ''),  # 用例ID
                    'title': case.get('title', ''),  # 用例标题
                    'precondition': case.get('precondition', ''),  # 前置条件
                    'steps': steps_str,  # 测试步骤（字符串格式）
                    'expected': case.get('expected', '')  # 预期结果
                }

                table_data.append(table_row)

        return table_data


if __name__ == "__main__":
    run_code = 0
