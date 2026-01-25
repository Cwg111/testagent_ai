# @FileName  :routes.py
# @Time      :2026/1/19 10:14
# @Author    :ChenWenGang
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json
import os
from src.generators.command_processor import CommandDispatcher
from src.paths import temp_path, index_html_path, static_path

# 初始化FastAPI应用
app = FastAPI()
command_dispatcher = CommandDispatcher()

# 静态资源路由
app.mount("/static", StaticFiles(directory=static_path), name="static")


# 根路径返回template/index.html
@app.get("/", response_class=HTMLResponse)
async def serve_fronted():
    with open(index_html_path, "r",encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)


# 跨域配置（解决前端后端域名不一致问题）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000"],  # 允许的源域名，*表示允许所有源
    allow_credentials=True,
    allow_methods=["*"],  # 允许的HTTP方法，*表示允许所有方法
    allow_headers=["*"],  # 允许的请求头，*表示允许所有头
)


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
        # 生成唯一文件名：时间戳+文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(temp_path, filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

    # 定义流式响应生成器
    def stream_response():
        for chunk in command_dispatcher.process_by_command(
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


@app.get("/export")
async def export_content(file_path: str = Query(...)):
    """
    前端调用接口：导出文件
    """
    if not os.path.exists(file_path):
        return {"status": "error", "data": "文件不存在"}
    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type="application/octet-stream"
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
