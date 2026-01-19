# @FileName  :paths.py
# @Time      :2026/1/19 9:55
# @Author    :ChenWenGang
import os

src_path = os.path.dirname(os.path.abspath(__file__))
base_path = os.path.dirname(src_path)
env_path = os.path.join(base_path, ".env")
config_yaml_path=os.path.join(base_path, "config.yaml")
generated_scripts_path=os.path.join(base_path, "generated_scripts")
reports_path=os.path.join(base_path, "reports")

# generated_scripts_path和reports_path不存在时，自动创建目录
for path in [generated_scripts_path, reports_path]:
    os.makedirs(path, exist_ok=True)


if __name__ == "__main__":
    print(base_path)
