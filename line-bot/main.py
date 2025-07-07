from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from handlers import handle_webhook
from file_service import file_service
import os
from pathlib import Path
import uuid
import uvicorn

app = FastAPI(title="LINE Bot API", version="1.0.0")

# アップロードディレクトリの作成
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)

# 静的ファイルの配信設定
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/samples", StaticFiles(directory="samples"), name="samples")

@app.post('/callback')
async def webhook(request: Request):
    """LINE Webhook エンドポイント"""
    return await handle_webhook(request)

@app.get("/media/{media_type}/{file_id}")
async def get_media_file(media_type: str, file_id: str):
    """メディアファイル（画像・動画・音声）の配信"""
    try:
        print(f"🔍 メディアファイル配信リクエスト: {media_type}/{file_id}")
        
        # ファイルを検索
        file_info = file_service.get_file_by_id(file_id)
        if not file_info:
            print(f"❌ ファイル情報が見つかりません: {file_id}")
            raise HTTPException(status_code=404, detail="File not found")
        
        print(f"📋 ファイル情報: {file_info}")
        
        # ファイルパスを解決
        file_path_str = file_info['file_path']
        file_path = Path(file_path_str)
        
        # 相対パスの場合は現在のディレクトリからの絶対パスに変換
        if not file_path.is_absolute():
            current_dir = Path.cwd()
            file_path = current_dir / file_path
            print(f"📁 絶対パスに変換: {file_path}")
        
        if not file_path.exists():
            print(f"❌ ファイルが存在しません: {file_path}")
            raise HTTPException(status_code=404, detail="File not found")
        
        print(f"✅ ファイル存在確認: {file_path}")
        
        # Content-Typeを設定
        content_type = file_info.get('content_type', 'application/octet-stream')
        
        print(f"📤 メディアファイル配信開始: {file_path}")
        
        # シンプルにファイルを返す
        return FileResponse(
            path=str(file_path),
            media_type=content_type
        )
        
    except HTTPException:
        # HTTPExceptionはそのまま再送出
        raise
    except Exception as e:
        print(f'❌ Error serving media file: {e}')
        print(f'❌ Exception type: {type(e)}')
        import traceback
        print(f'❌ Traceback: {traceback.format_exc()}')
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/files/{file_id}")
async def get_file(file_id: str):
    """ファイルの配信（PDF、ZIP、テキストなど）"""
    try:
        print(f"🔍 ファイル配信リクエスト: {file_id}")
        
        # ファイルを検索
        file_info = file_service.get_file_by_id(file_id)
        if not file_info:
            print(f"❌ ファイル情報が見つかりません: {file_id}")
            raise HTTPException(status_code=404, detail="File not found")
        
        print(f"📋 ファイル情報: {file_info}")
        
        # ファイルパスを解決
        file_path_str = file_info['file_path']
        file_path = Path(file_path_str)
        
        # 相対パスの場合は現在のディレクトリからの絶対パスに変換
        if not file_path.is_absolute():
            current_dir = Path.cwd()
            file_path = current_dir / file_path
            print(f"📁 絶対パスに変換: {file_path}")
        
        if not file_path.exists():
            print(f"❌ ファイルが存在しません: {file_path}")
            raise HTTPException(status_code=404, detail="File not found")
        
        print(f"✅ ファイル存在確認: {file_path}")
        
        # Content-Typeを設定
        content_type = file_info.get('content_type', 'application/octet-stream')
        
        print(f"📤 ファイル配信開始: {file_path}")
        
        # シンプルにファイルを返す
        return FileResponse(
            path=str(file_path),
            media_type=content_type
        )
        
    except HTTPException:
        # HTTPExceptionはそのまま再送出
        raise
    except Exception as e:
        print(f'❌ Error serving file: {e}')
        print(f'❌ Exception type: {type(e)}')
        import traceback
        print(f'❌ Traceback: {traceback.format_exc()}')
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/files")
async def list_files():
    """ファイル一覧取得API（デバッグ用）"""
    try:
        files = file_service.list_files()
        return {
            "files": files,
            "count": len(files)
        }
    except Exception as e:
        print(f'Error listing files: {e}')
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/files/{file_id}")
async def get_file_info(file_id: str):
    """ファイル情報取得API（デバッグ用）"""
    try:
        file_info = file_service.get_file_by_id(file_id)
        if not file_info:
            raise HTTPException(status_code=404, detail="File not found")
        
        return file_info
    except Exception as e:
        print(f'Error getting file info: {e}')
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/")
async def root():
    """APIドキュメント"""
    return {
        "message": "LINE Bot API",
        "version": "1.0.0",
        "endpoints": {
            "webhook": "POST /callback",
            "media_files": "GET /media/{media_type}/{file_id}",
            "files": "GET /files/{file_id}",
            "api_files": "GET /api/files",
            "api_file_info": "GET /api/files/{file_id}"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)