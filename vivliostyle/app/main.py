from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import tempfile
import os
import subprocess
import logging
from pathlib import Path

from .pdf_service import PDFService
from .schemas import GenerateRequest, GenerateResponse

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="雑誌風PDF自動生成サービス",
    description="Vivliostyle CLIを使用して雑誌風PDFを生成するサービス",
    version="1.0.0"
)

# PDFサービスインスタンス
pdf_service = PDFService()

@app.get("/")
async def root():
    """ヘルスチェックエンドポイント"""
    return {"message": "雑誌風PDF自動生成サービス", "status": "running"}

@app.get("/templates")
async def list_templates():
    """利用可能なテンプレート一覧を取得"""
    templates = pdf_service.get_available_templates()
    return {"templates": templates}

@app.post("/generate", response_model=GenerateResponse)
async def generate_pdf(request: GenerateRequest):
    """PDF生成エンドポイント"""
    try:
        logger.info(f"PDF生成開始: template_id={request.template_id}")
        
        # PDF生成
        pdf_path = await pdf_service.generate_pdf(
            template_id=request.template_id,
            payload=request.payload
        )
        
        # ファイルサイズ確認
        file_size = os.path.getsize(pdf_path)
        logger.info(f"PDF生成完了: {pdf_path}, サイズ: {file_size} bytes")
        
        # ストリーミングレスポンス
        def iterfile():
            with open(pdf_path, "rb") as f:
                yield from f
            # 一時ファイル削除
            os.unlink(pdf_path)
        
        return StreamingResponse(
            iterfile(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=magazine_{request.template_id}.pdf"
            }
        )
        
    except Exception as e:
        logger.error(f"PDF生成エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF生成に失敗しました: {str(e)}")

@app.get("/health")
async def health_check():
    """システムヘルスチェック"""
    try:
        # Vivliostyle CLIの確認
        result = subprocess.run(
            ["vivliostyle", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        vivliostyle_available = result.returncode == 0
        
        return {
            "status": "healthy",
            "vivliostyle_cli": "available" if vivliostyle_available else "not_available",
            "vivliostyle_version": result.stdout.strip() if vivliostyle_available else None
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 