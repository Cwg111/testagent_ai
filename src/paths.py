# @FileName  :paths.py
# @Time      :2026/1/19 9:55
# @Author    :ChenWenGang
import os
from pathlib import Path

src_path = os.path.dirname(os.path.abspath(__file__))
base_path = os.path.dirname(src_path)
env_path = os.path.join(base_path, ".env")
config_yaml_path = os.path.join(base_path, "config.yaml")
generated_scripts_path = os.path.join(base_path, "generated_scripts")
test_file_path = os.path.join(base_path, "test_file")
temp_path = os.path.join(base_path, "temp_uploads")  # 用来存储用户上传的文件
case_path = os.path.join(base_path, "generated_cases")  # 用来存储生成的测试用例
# 用来存储生成的自动化测试脚本
web_script_path = os.path.join(generated_scripts_path, "web_scripts")
api_script_path = os.path.join(generated_scripts_path, "api_scripts")
# 用来存储生成的需求检查清单
requirement_checklist_path = os.path.join(base_path, "generated_checklist")
# 用来存储通用大模型生成的纯文本内容
general_answers_path=os.path.join(base_path, "general_answers")
# 模板文件路径
index_html_path = os.path.join(base_path, "templates", "index.html")
# 静态文件（static）路径
static_path = os.path.join(base_path, "static")

# 目录不存在时，自动创建目录，这是创建目录，如果用来创建文件会报错
for path in [generated_scripts_path, test_file_path, temp_path, case_path, web_script_path, api_script_path,
             requirement_checklist_path, general_answers_path]:
    os.makedirs(path, exist_ok=True)

# 只创建空文件，文件已存在则不做任何操作（不会覆盖）
Path(env_path).touch(exist_ok=True)

if __name__ == "__main__":
    print(base_path)
