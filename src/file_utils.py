# @FileName  :file_utils.py
# @Time      :2026/1/19 9:55
# @Author    :ChenWenGang

import os
import pandas as pd
import markdown_it
from typing import Literal
import pdfplumber
import docx2txt


class FileUtils:
    """通用文件解析工具（仅支持Windows环境），提取文本内容"""
    # 支持的格式：txt/md/doc/docx/pdf/xls/xlsx
    SUPPORTED_FILE_TYPES = [".txt", ".md", ".docx", ".pdf", ".xls", ".xlsx", ".json"]

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
    def parse_docx(file_path: str) -> str:
        """
        用docx2txt解析docx文件（仅提取文本+表格，完全跳过图片）
        """
        try:
            # 核心：仅传文件路径，不传图片保存目录 → 自动跳过图片处理
            # docx2txt.process默认会提取表格（转为文本表格）、段落，忽略图片
            text = docx2txt.process(file_path)

            # 清理多余空行和首尾空格，提升可读性
            cleaned_text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
            return cleaned_text
        except Exception as e:
            raise RuntimeError(f"解析docx文件失败：{str(e)}")

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
        engine: Literal["xlrd", "openpyxl"] = "xlrd" if ext == ".xls" else "openpyxl"  # type: ignore

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
        elif ext == ".docx":
            return FileUtils.parse_docx(file_path)
        elif ext == ".pdf":
            return FileUtils.parse_pdf(file_path)
        elif ext in [".xls", ".xlsx"]:
            return FileUtils.parse_excel(file_path)
        elif ext == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            raise ValueError(f"不支持的文件类型：{ext}，仅支持{FileUtils.SUPPORTED_FILE_TYPES}")


if __name__ == "__main__":
    # 测试四种格式文档的读取，测试文件在reports目录下
    # from src.paths import test_file_path
    # test_file = os.path.join(test_file_path, "test.xlsx")
    # print(FileUtils.parse_file(test_file))
    pass
