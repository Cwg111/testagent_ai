# @FileName  :file_utils.py
# @Time      :2026/1/19 9:55
# @Author    :ChenWenGang

import os
import pandas as pd
from docx import Document
import markdown_it
from typing import Literal
import pdfplumber
import win32com.client as win32  # Windows专属：解析.dox格式


class FileUtils:
    """通用文件解析工具（仅支持Windows环境），提取文本内容"""
    # 支持的格式：txt/md/doc/docx/pdf/xls/xlsx
    SUPPORTED_FILE_TYPES = ["txt", "md", "doc", "docx", "pdf", "xls", "xlsx"]

    @staticmethod
    def validate_file_type(file_path: str) -> bool:
        """
        验证文件类型
        :param file_path: 文件路径
        :return: 是否是支持的文件类型
        """
        file_type = os.path.splitext(file_path)[1].lower()
        return file_type in FileUtils.SUPPORTED_FILE_TYPES

    @staticmethod
    def parse_doc(file_path: str) -> str:
        """
        解析.doc格式文件（仅Window环境，依赖pywin32）
        :param file_path: 文件路径
        :return: 处理好的文本内容
        """
        word = None
        try:
            # Windows COM接口调用Word解析.doc
            word = win32.Dispatch("Word.Application")
            word.Visible = False  # 后台运行，不显示word窗口
            word.DisplayAlerts = 0  # 屏蔽word弹窗，比如格式兼容窗口
            doc = word.Documents.Open(os.path.abspath(file_path))
            text = doc.Content.Text.strip()
            doc.Close(SaveChange=0)  # 不保存修改
            return text
        except Exception as e:
            raise RuntimeError(f"解析.doc文件失败：{e}\n请确认：1.已安装Microsoft Word;2.已安装pywin32")
        finally:
            if word:
                word.Quit()

    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """
        解析.pdf格式文件
        :param file_path: 文件路径
        :return: 处理好的文本内容
        """
        text_content = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text.strip())
            return "\n\n".join(text_content)  # 每页空两行分隔，保留结构
        except Exception as e:
            raise RuntimeError(f"解析.pdf文件失败：{e}")

    @staticmethod
    def parse_excel(file_path: str) -> str:
        """
        解析excel文件（.xls/.xlsx）
        :param file_path: 文件路径
        :return: 处理好的文本内容
        """
        text_content = []
        ext = os.path.splitext(file_path)[1].lower()

        # 适配Excel引擎，xls用xlrd，xlsx用openpyxl，使用Literal限制engine只能取xlrd或openpyxl
        engine: Literal["xlrd", "openpyxl"] = "xlrd" if ext == ".xls" else "openpyxl"

        try:
            excel_file = pd.ExcelFile(file_path, engine=engine)
            for sheet_name in excel_file.sheet_names:
                # 读取sheet，跳过空行、填充空值
                df = pd.read_excel(
                    file_path,
                    sheet_name=sheet_name,
                    engine=engine
                ).fillna("")
                if df.empty:
                    continue

                # 拼接Sheet名称和表格内容，保留行列结构
                text_content.append(f"【Sheet：{sheet_name}】")
                text_content.append(df.to_string(index=False, header=True))
                text_content.append("-" * 60)  # 分隔不同sheet
            return "\n".join(text_content) if text_content else "Excel文件无有效内容"
        except Exception as e:
            raise RuntimeError(f"解析.xlsx文件失败：{e}")

    @staticmethod
    def parse_file(file_path: str) -> str:
        """
        解析文件，提取文本内容
        :param file_path: 文件路径
        :return: 文本内容
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在：{file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        if not FileUtils.validate_file_type(file_path):
            raise ValueError(f"不支持的文件类型：{ext}，仅支持{FileUtils.SUPPORTED_FILE_TYPES}")

        # 按格式解析文件
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        elif ext == ".md":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        elif ext == ".doc":
            return FileUtils.parse_doc(file_path)
        elif ext == ".docx":
            document = Document(file_path)
            return "\n".join([para.text.strip() for para in document.paragraphs if para.text.strip()])
        elif ext == ".pdf":
            return FileUtils.parse_pdf(file_path)
        elif ext in [".xls", ".xlsx"]:
            return FileUtils.parse_excel(file_path)
        else:
            raise ValueError(f"不支持的文件类型：{ext}，仅支持{FileUtils.SUPPORTED_FILE_TYPES}")


if __name__ == "__main__":
    run_code = 0
