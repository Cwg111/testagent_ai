# @FileName  :routes.py
# @Time      :2026/1/19 10:14
# @Author    :ChenWenGang
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
import json
from src.generators.case_web_generator import TestGenerator

app = FastAPI()
test_generator = TestGenerator()

@app.post("/process-command")
async def process_command(
    command_text: str = Form(...),
    session_id: str = Form(None),
    file: UploadFile = File(None)
):
    """
    前端调用接口：接收指令、会话ID、上传文件，返回流式响应
    """
    # 保存上传文件到本地（示例逻辑，需根据实际路径调整）
    file_path = ""
    if file:
        file_path = f"./uploads/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())

    # 定义流式响应生成器
    def stream_response():
        for chunk in test_generator.process_by_command(
            file_path=file_path,
            command_text=command_text,
            session_id=session_id
        ):
            # 转换为JSON字符串（前端可解析）
            yield json.dumps(chunk, ensure_ascii=False) + "\n"

    # 返回流式响应
    return StreamingResponse(
        stream_response(),
        media_type="application/x-ndjson"  # 每行一个JSON，前端逐行解析
    )

if __name__ == "__main__":
    run_code = 0
