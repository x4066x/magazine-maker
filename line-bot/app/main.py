from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn
import logging

from .config import settings
from .api import router

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# FastAPIアプリケーション
app = FastAPI(title="LINE Bot API", version="1.0.0")

# アップロードディレクトリの作成
settings.UPLOADS_DIR.mkdir(exist_ok=True)
settings.SAMPLES_DIR.mkdir(exist_ok=True)

# LIFFディレクトリの作成
liff_dir = Path(__file__).parent.parent / "liff"
liff_dir.mkdir(exist_ok=True)

# 静的ファイルの配信設定
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOADS_DIR)), name="uploads")
app.mount("/samples", StaticFiles(directory=str(settings.SAMPLES_DIR)), name="samples")
app.mount("/liff", StaticFiles(directory=str(liff_dir)), name="liff")

# APIルーターを登録
app.include_router(router)

def start_server():
    """サーバーを起動"""
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)

if __name__ == "__main__":
    start_server()

