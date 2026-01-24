# @FileName  :case_web_generator.py
# @Time      :2026/1/19 10:12
# @Author    :ChenWenGang
import datetime
import json
from typing import Dict, Generator
from openpyxl.styles import Alignment
import pandas as pd

from src.llm.client import LLMClient
from src.command_parser import CommandParser
from src.context_manager import session_manager
from src.file_utils import FileUtils
from src.paths import *


class TestGenerator:
    def __init__(self):
        self.llm_client = LLMClient()
        self.command_parser = CommandParser()

    def process_by_command(self, file_path: str, command_text: str, session_id: str = None) -> Generator[
        Dict, None, None]:
        """
        核心入口，生成测试用例/测试脚本，逐段返回结果
        :param file_path: 需求文档/用例文件路径
        :param command_text: 用户输入的自然语言指令
        :param session_id: 当前会话ID，默认为None
        :yield: 流式返回字典，格式：
        {
            "type":"status"/"content"/"final"/"error"
            "session_id":str,
            "data":状态信息/实时内容/最终结果/错误信息
        }
        """
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
                yield from self._handle_generate_case(file_path, current_session_id)
            elif intent == "generate_web_script":
                yield from self._handle_generate_script(use_context, file_path, current_session_id)
            else:
                yield {
                    "type": "error",
                    "session_id": current_session_id,
                    "data": f"暂时没法帮你处理「{command_text}」这个指令哦～我目前可以帮你生成测试用例、web/接口自动化测试脚本，"
                            f"还有需求检查清单，"
                            f"换个相关指令试试吧～"
                }
                return
        except Exception as e:
            yield {
                "type": "error",
                "session_id": current_session_id,
                "data": f"生成失败：{str(e)}"
            }
            return

    def _handle_generate_case(self, file_path: str, session_id: str = None) -> Generator[Dict, None, None]:
        """
        流式生成测试用例（返回表格渲染数据）
        :param file_path: 需求文档路径
        :param session_id: 当前会话的ID
        :yield: 流式返回字典，格式：
        {
            "type":"status"/"content"/"final"/"error/table_display"
            "session_id":str,
            "data":状态信息/实时内容/最终结果/错误信息
        }
        """
        if not file_path:
            yield {
                "type": "error",
                "session_id": session_id,
                "data": "生成测试用例需要上传需求文档"
            }
            return  # 当解析失败时，返回错误信息，不再执行后续代码
        # 返回状态，开始解析需求文档
        yield {
            "type": "status",
            "session_id": session_id,
            "data": "开始解析需求文档，生成测试用例中..."
        }
        requirement_text = FileUtils.parse_file(file_path)
        # 流式获取LLM生成的测试用例JSON（实时返回内容）
        case_json_stream = self.llm_client.parse_requirement_to_testcase_stream(requirement_text)
        full_case_json = ""
        for chunk in case_json_stream:
            full_case_json += chunk
            yield {
                "type": "success",
                "session_id": session_id,
                "data": chunk  # 前端实时显示JSON片段
            }
        # 解析用例JSON，生成表格数据
        try:
            case_data = json.loads(full_case_json)
        except Exception as e:
            yield {
                "type": "error",
                "session_id": session_id,
                "data": f"测试用例解析失败：{str(e)}"
            }
            return  # 当解析失败时，返回错误信息，不再执行后续代码
        # 保存用例文件为xlsx格式

        table_data = self._convert_to_table_format(case_data)
        save_case_path = self._generate_testcase_excel(table_data, case_data)
        # with open(save_case_path, "w", encoding="utf-8") as f:
        #     json.dump(table_data, f, indent=2, ensure_ascii=False)  # type: ignore

        # 本次会话记住生成的用例路径，下次请求时使用
        session_manager.save_case_path(session_id, save_case_path)
        # 返回最终结果（表格数据+文件路径）
        yield {
            "type": "final",
            "session_id": session_id,
            "data": {
                "status": "success",
                "message": "生成测试用例成功，将为您用表格展示",
                "file_path": save_case_path,
                "table_data": table_data
            }
        }

    def _handle_generate_script(self, use_context: bool, file_path: str = None, session_id: str = None) -> Generator[
        Dict, None, None]:
        """
        流式生成生成Selenium+pytest测试脚本
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
        # 确定用例路径
        case_path_target = ""
        if use_context:
            yield {
                "type": "status",
                "session_id": session_id,
                "data": "回答这个问题需要使用上下文，正读取上下文中..."
            }
            case_path_target = session_manager.get_case_path(session_id)
            if not case_path_target:
                yield {
                    "type": "error",
                    "session_id": session_id,
                    "data": "本次会话未生成测试用例，请先上传需求文档生成测试用例"
                }
                return  # 当解析失败时，返回错误信息，不再执行后续代码
        else:
            if not file_path:
                yield {
                    "type": "error",
                    "session_id": session_id,
                    "data": "生成测试脚本需要上传测试用例"
                }
                return  # 当解析失败时，返回错误信息，不再执行后续代码
            case_path_target = file_path

        # 返回状态，开始解析用例
        yield {
            "type": "status",
            "session_id": session_id,
            "data": "开始解析测试用例，生成自动化测试脚本中..."
        }

        # 解析用例，生成Selenium+pytest脚本
        case_text = FileUtils.parse_file(case_path_target)
        script_stream = self.llm_client.testcase_to_web_script(case_text)
        full_script = ""
        for chunk in script_stream:
            full_script += chunk
            yield {
                "type": "success",
                "session_id": session_id,
                "data": chunk  # 前端实时显示脚本片段
            }

        # 保存脚本文件
        script_filename = f"test_web_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.py"
        save_script_path = os.path.join(web_script_path, script_filename)
        with open(save_script_path, "w", encoding="utf-8") as f:
            f.write(full_script)

        # 返回最终结果
        yield {
            "type": "final",
            "session_id": session_id,
            "data": {
                "status": "success",
                "message": "生成自动化测试脚本成功",
                "file_path": save_script_path,
                "script_content": full_script
            }
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
                # 将步骤列表转换为字符串（用英文逗号连接）
                steps_str = ','.join(case.get('steps', []))

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

    @staticmethod
    def _generate_testcase_excel(table_data: list, case_data: Dict) -> str:
        """
        专用函数：基于table_data生成和截图一致的Excel文件
        :param table_data: 已转换的前端表格数据（_convert_to_table_format的返回值）
        :param case_data: 原始JSON数据（仅用于获取测试套件名称）
        :return: Excel保存路径
        """
        # 1. 处理table_data，映射列名+格式化测试步骤
        excel_rows = []
        for row in table_data:
            # 把table_data的字段映射为截图的Excel列名
            # 处理测试步骤：逗号分隔的字符串 → 带序号+换行的格式（匹配截图）
            steps_list = row['steps'].split(',')  # 拆分逗号分隔的步骤为列表
            steps_str = ""
            for idx, step in enumerate(steps_list, 1):
                steps_str += f"{idx}.{step.strip()};\n"  # 1.打开登录页面;\n2.输入账号...
            steps_str = steps_str.strip()  # 去掉最后一个换行

            # 构建Excel行数据（列名完全匹配截图）
            excel_row = {
                "功能模块": row['feature'],  # table_data的feature → 功能模块
                "模块描述": row['module_desc'],  # table_data的module_desc → 模块描述
                "用例ID": row['case_id'],  # table_data的case_id → 用例ID
                "用例标题": row['title'],  # table_data的title → 用例标题
                "前置条件": row['precondition'],  # table_data的precondition → 前置条件
                "测试步骤": steps_str,  # 格式化后的测试步骤
                "预期结果": row['expected']  # table_data的expected → 预期结果
            }
            excel_rows.append(excel_row)

        # 2. 生成DataFrame并保存为Excel
        df = pd.DataFrame(excel_rows)
        test_suite = case_data.get("test_suite", "未知套件")
        case_filename = f"{test_suite}_case_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        save_case_path = os.path.join(case_path, case_filename)

        # 3. 调整Excel样式（匹配截图）
        with pd.ExcelWriter(save_case_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='测试用例', index=False)
            worksheet = writer.sheets['测试用例']

            # 设置列宽（匹配截图比例）
            column_widths = {
                "功能模块": 10,
                "模块描述": 30,
                "用例ID": 10,
                "用例标题": 20,
                "前置条件": 20,
                "测试步骤": 40,
                "预期结果": 30
            }
            for col_name, width in column_widths.items():
                col_idx = df.columns.get_loc(col_name) + 1  # openpyxl列索引从1开始
                worksheet.column_dimensions[chr(64 + col_idx)].width = width

            # 单元格自动换行+顶部对齐（匹配截图）
            for excel_row in worksheet.iter_rows():
                for cell in excel_row:
                    cell.alignment = Alignment(wrap_text=True, vertical='top')

        return save_case_path


if __name__ == "__main__":
    # 测试需求文档生成测试用例
    test_file_path = os.path.join(test_file_path, "需求文档.docx")
    generator = TestGenerator().process_by_command(test_file_path, "你好", session_id=None)
    for chunk in generator:
        print(chunk)
    # # 测试用例生成Selenium+pytest脚本
    # test_file_path = os.path.join(test_file_path, "电商系统V2.0测试用例.xlsx")
    # generator = TestGenerator().process_by_command(test_file_path, "生成自动化测试脚本", session_id=None)
    # for chunk in generator:
    #     print(chunk)
    pass
