# @FileName  :paths.py
# @Time      :2026/1/19 9:55
# @Author    :ChenWenGang
import os

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
# 模板文件路径
index_html_path = os.path.join(base_path, "templates", "index.html")
# 静态文件（static）路径
static_path = os.path.join(base_path, "static")

# 目录不存在时，自动创建目录
for path in [generated_scripts_path, test_file_path, temp_path, case_path, web_script_path, api_script_path]:
    os.makedirs(path, exist_ok=True)

if __name__ == "__main__":
    print(base_path)
