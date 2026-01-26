# @FileName  :main.py
# @Time      :2026/1/26 9:16
# @Author    :ChenWenGang
import uvicorn
from src.api.routes import app  # 导入routes.py中定义的FastAPI应用实例

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
