from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn

from .config import settings
from .api import router

# FastAPIアプリケーション
app = FastAPI(title="LINE Bot API", version="1.0.0")

# アップロードディレクトリの作成
settings.UPLOADS_DIR.mkdir(exist_ok=True)
settings.SAMPLES_DIR.mkdir(exist_ok=True)

# 静的ファイルの配信設定
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOADS_DIR)), name="uploads")
app.mount("/samples", StaticFiles(directory=str(settings.SAMPLES_DIR)), name="samples")

# APIルーターを登録
app.include_router(router)

def start_server():
    """サーバーを起動"""
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)

if __name__ == "__main__":
    start_server()

