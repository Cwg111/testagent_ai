# @FileName  :config_loader.py
# @Time      :2026/1/9 10:52
# @Author    :ChenWenGang
import os
import yaml
from dotenv import load_dotenv

# 加载env文件
load_dotenv()
# 定义项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 加载yaml 文件
with open(os.path.join(PROJECT_ROOT, "config.yaml"), "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)
# 替换敏感配置
config["llm"]["api_key"] = os.getenv("OPENAI_API_KEY")
config["llm"]["base_url"] = os.getenv("OPENAI_BASE_URL")

config["paths"] = {
    "script_save": os.path.join(PROJECT_ROOT, "generated_scripts"),
    "report_save": os.path.join(PROJECT_ROOT, "reports")
}

# 目录不存在时，自动创建目录
for path in config["paths"].values():
    os.makedirs(path, exist_ok=True)

CONFIG = config

if __name__ == "__main__":
    print(CONFIG)
