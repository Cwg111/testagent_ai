# @FileName  :product_generator.py
# @Time      :2026/1/19 10:13
# @Author    :ChenWenGang
import datetime
import json
from typing import Dict, Generator
from openpyxl.styles import Alignment
import pandas as pd
from src.llm.client import LLMClient
from src.context_manager import session_manager
from src.file_utils import FileUtils
from src.paths import *


class ProductGenerator:
    def __init__(self,llm_client:LLMClient):
        self.llm_client = llm_client

    def handle_generate_checklist(self, file_path: str, session_id: str ) -> Generator[Dict, None, None]:
        """
        流式生成需求检查清单（返回表格渲染数据）
        :param file_path: 需求文档路径
        :param session_id: 当前会话的ID
        :yield: 流式返回字典，格式：
        {
            "type":"status"/"json_chunk"/"final"/"error"
            "session_id":str,
            "data":状态信息/实时内容/最终结果/错误信息
        }
        """
        if not file_path:
            yield {
                "type": "error",
                "session_id": session_id,
                "data": "生成需求检查清单需要上传需求文档"
            }
            return  # 当解析失败时，返回错误信息，不再执行后续代码
        # 返回状态，开始解析需求文档
        yield {
            "type": "status",
            "session_id": session_id,
            "data": "开始解析需求文档，生成检查清单中..."
        }
        requirement_text = FileUtils.parse_file(file_path)
        # 流式获取LLM生成的检查清单JSON（实时返回内容）
        checklist_json_stream = self.llm_client.parse_requirement_to_checklist_stream(requirement_text)
        full_checklist_json = ""
        for chunk in checklist_json_stream:
            full_checklist_json += chunk
            yield {
                "type": "json_chunk",
                "session_id": session_id,
                "data": chunk  # 前端不显示JSON片段
            }
        # 解析检查清单JSON，生成表格数据
        try:
            checklist_data = json.loads(full_checklist_json)
        except Exception as e:
            yield {
                "type": "error",
                "session_id": session_id,
                "data": f"测试用例解析失败：{str(e)}"
            }
            return  # 当解析失败时，返回错误信息，不再执行后续代码
        # 保存需求检查清单文件为xlsx格式

        table_data = self._convert_to_table_format(checklist_data)
        save_checklist_path = self._generate_checklist_excel(table_data, checklist_data)


        # 本次会话记住生成的用例路径，下次请求时使用
        session_manager.save_case_path(session_id, save_checklist_path)
        # 返回最终结果（表格数据+文件路径）
        yield {
            "type": "final",
            "session_id": session_id,
            "data": {
                "status": "success",
                "message": "生成需求检查清单成功，将为您用表格展示",
                "file_path": save_checklist_path,
                "checklist_table_data": table_data
            }
        }

    @staticmethod
    def _convert_to_table_format(checklist_data: Dict) -> list:
        """
        将大模型返回的测试用例数据转换为前端表格格式
        :param checklist_data: 大模型返回的需求检查清单数据
        :return: 表格格式的测试用例数据
        """
        table_data = []

        # 获取所有模块
        modules = checklist_data.get('check_modules', [])

        for module in modules:
            feature = module.get('check_category', '未知模块')
            module_desc = module.get('module_desc', '')
            check_items = module.get('check_items', [])

            # 遍历模块下的所有检查清单
            for item in check_items:
                # 将步骤列表转换为字符串（用英文逗号连接）
                items_str = ','.join(item.get('check_item', []))

                # 构建表格行数据
                table_row = {
                    'check_modules': feature,  # 功能模块
                    'module_desc': module_desc,  # 模块描述
                    'check_item': items_str,  # 检查事项步骤（字符串格式）
                    # 对应需求点
                    'corresponding_requirement': item.get('corresponding_requirement', ''),
                    'check_standard': item.get('check_standard', ''), # 检查标准
                    'is_passed': item.get('is_passed', '')  # 核验结果，默认为空
                }

                table_data.append(table_row)

        return table_data

    @staticmethod
    def _generate_checklist_excel(table_data: list, checklist_data: Dict) -> str:
        """
        专用函数：基于table_data生成Excel文件
        :param table_data: 已转换的前端表格数据（_convert_to_table_format的返回值）
        :param checklist_data: 原始JSON数据（仅用于获取检查清单名称）
        :return: Excel保存路径
        """
        # 1. 处理table_data，映射列名+格式化检查事项
        excel_rows = []
        for row in table_data:
            # 把table_data的字段映射为截图的Excel列名
            # 处理检查事项：逗号分隔的字符串 → 带序号+换行的格式（匹配截图）
            item_list = row['check_item'].split(',')  # 拆分逗号分隔的步骤为列表
            item_str = ""
            for idx, item in enumerate(item_list, 1):
                item_str += f"{idx}.{item.strip()};\n"  # 1.打开登录页面;\n2.输入账号...
            item_str = item_str.strip()  # 去掉最后一个换行

            # 构建Excel行数据（列名完全匹配截图）
            excel_row = {
                "检查类别": row['check_modules'],  # table_data的feature → 检查类别
                "类别描述": row['module_desc'],  # table_data的module_desc → 类别描述
                "检查事项步骤": item_str,  # 格式化后的检查事项步骤
                "对应需求点编号": row['corresponding_requirement'],
                "检查标准": row['check_standard'],
                "是否通过": row['is_passed'],
            }
            excel_rows.append(excel_row)

        # 2. 生成DataFrame并保存为Excel
        df = pd.DataFrame(excel_rows)
        checklist_name = checklist_data.get("checklist_name", "未知项目需求检查清单")
        checklist_filename = f"{checklist_name}_checklist_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        save_checklist_path = os.path.join(requirement_checklist_path, checklist_filename)

        # 3. 调整Excel样式
        with pd.ExcelWriter(save_checklist_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='需求检查清单', index=False)
            worksheet = writer.sheets['需求检查清单']

            # 设置列宽
            column_widths = {
                "检查类别": 20,
                "类别描述": 30,
                "检查事项步骤": 40,
                "对应需求点编号": 10,
                "检查标准": 30,
                "是否通过": 20
            }
            for col_name, width in column_widths.items():
                col_idx = df.columns.get_loc(col_name) + 1  # type: ignore
                worksheet.column_dimensions[chr(64 + col_idx)].width = width

            # 单元格自动换行+顶部对齐（匹配截图）
            for excel_row in worksheet.iter_rows():
                for cell in excel_row:
                    cell.alignment = Alignment(wrap_text=True, vertical='top')

        return save_checklist_path

if __name__ == "__main__":
    run_code = 0
