from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from handlers import handle_webhook
from file_service import file_service
import os
from pathlib import Path

app = FastAPI(title="LINE Bot with File Support", version="1.0.0")

# アップロードディレクトリの作成
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)

# 静的ファイルの配信設定
app.mount("/files", StaticFiles(directory="uploads"), name="files")
app.mount("/samples", StaticFiles(directory="samples"), name="samples")

@app.post('/callback')
async def webhook(request: Request):
    """LINE Webhook エンドポイント"""
    return await handle_webhook(request)

@app.get("/media/{media_type}/{file_id}")
async def get_media_file(media_type: str, file_id: str):
    """メディアファイル配信 API（画像、動画、音声用）"""
    try:
        file_info = file_service.get_file_by_id(file_id)
        
        if not file_info:
            raise HTTPException(status_code=404, detail="ファイルが見つかりません")
        
        # メディアタイプの検証
        if media_type not in ['image', 'video', 'audio']:
            raise HTTPException(status_code=400, detail="無効なメディアタイプです")
        
        file_path = file_info['file_path']
        
        if not Path(file_path).exists():
            raise HTTPException(status_code=404, detail="ファイルが見つかりません")
        
        return FileResponse(
            path=file_path,
            media_type=file_info['content_type'],
            filename=Path(file_path).name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイル取得エラー: {str(e)}")

@app.get("/files/{file_id}")
async def get_file(file_id: str):
    """ファイル配信 API"""
    try:
        file_info = file_service.get_file_by_id(file_id)
        
        if not file_info:
            raise HTTPException(status_code=404, detail="ファイルが見つかりません")
        
        file_path = file_info['file_path']
        
        if not Path(file_path).exists():
            raise HTTPException(status_code=404, detail="ファイルが見つかりません")
        
        return FileResponse(
            path=file_path,
            media_type=file_info['content_type'],
            filename=Path(file_path).name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイル取得エラー: {str(e)}")

@app.get("/api/files")
async def list_files():
    """ファイル一覧 API（デバッグ・管理用）"""
    try:
        files = file_service.list_files()
        base_url = os.environ.get('BASE_URL', 'http://localhost:8000')
        
        # 各ファイルにURLを追加
        for file_info in files:
            file_info['file_url'] = file_service.get_file_url(file_info['file_id'], base_url)
        
        return {
            "files": files,
            "total_count": len(files)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイル一覧取得エラー: {str(e)}")

@app.get("/api/files/{file_id}")
async def get_file_info(file_id: str):
    """ファイル情報取得 API（デバッグ・管理用）"""
    try:
        file_info = file_service.get_file_by_id(file_id)
        
        if not file_info:
            raise HTTPException(status_code=404, detail="ファイルが見つかりません")
        
        base_url = os.environ.get('BASE_URL', 'http://localhost:8000')
        file_info['file_url'] = file_service.get_file_url(file_id, base_url)
        
        return file_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイル情報取得エラー: {str(e)}")

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "LINE Bot with File Support",
        "version": "2.0.0",
        "description": "LINE Botでファイル受信・送信・AI生成をサポート",
        "endpoints": {
            "webhook": "/callback",
            "files": "/files/{file_id}",
            "media": "/media/{media_type}/{file_id}",
            "api_files": "/api/files",
            "api_file_info": "/api/files/{file_id}"
        },
        "supported_features": [
            "テキストメッセージ処理",
            "画像・動画・音声・ファイル受信",
            "AI生成ファイル送信",
            "ChatGPT統合"
        ]
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)