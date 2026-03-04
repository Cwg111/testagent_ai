# @FileName  :config.py
# @Time      :2026/1/19 9:55
# @Author    :ChenWenGang
import yaml
import os
from dotenv import load_dotenv
from .paths import env_path, config_yaml_path

# 加载env文件
load_dotenv(dotenv_path=env_path)
# 加载yaml文件
with open(config_yaml_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)
# 替换敏感配置
config["llm"]["api_key"] = os.getenv("OPENAI_API_KEY")
config["llm"]["base_url"] = os.getenv("OPENAI_BASE_URL")

CONFIG = config

if __name__ == "__main__":
    run_code=0
