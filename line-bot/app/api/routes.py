from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel
from typing import Dict, Any, Optional
from ..handlers import handle_webhook
from ..services import file_service
from ..services.quick_memoir_service import quick_memoir_service
from ..services.openai_service import openai_service
from ..services.line_service import send_push_message
from ..services.media_template_schema import get_template
from ..config import settings

router = APIRouter()

# リクエストモデル
class MemoirSaveRequest(BaseModel):
    data: Dict[str, Any]

class TextGenerationRequest(BaseModel):
    type: str  # "profile" | "timeline_description" | "spread_story" | "single_description"
    data: Dict[str, Any]

class MediaMemoirSaveRequest(BaseModel):
    title: str
    author: str
    spread_text: str  # 格言・ひとこと（短文）
    single_title: str = ""
    single_text: str

@router.post('/callback')
async def webhook(request: Request):
    """LINE Webhook エンドポイント"""
    return await handle_webhook(request)

@router.get("/media/{media_type}/{file_id}")
async def get_media_file(
    media_type: str, 
    file_id: str,
    user_id: Optional[str] = None,
    group_id: Optional[str] = None
):
    """メディアファイル（画像・動画・音声）の配信
    
    Args:
        media_type: メディアタイプ
        file_id: ファイルID
        user_id: リクエストユーザーID（オプション）
        group_id: リクエストグループID（オプション）
    """
    try:
        print(f"🔍 メディアファイル配信リクエスト: {media_type}/{file_id}")
        print(f"👤 アクセス制御: user_id={user_id}, group_id={group_id}")
        
        # ファイルを検索（アクセス制御付き）
        file_info = file_service.get_file_by_id(
            file_id=file_id,
            requester_user_id=user_id,
            requester_group_id=group_id
        )
        if not file_info:
            print(f"❌ ファイル情報が見つからないか、アクセス権限がありません: {file_id}")
            raise HTTPException(status_code=404, detail="File not found or access denied")
        
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

@router.get("/files/{file_id}")
async def get_file(
    file_id: str,
    user_id: Optional[str] = None,
    group_id: Optional[str] = None
):
    """ファイルの配信（PDF、ZIP、テキストなど）
    
    Args:
        file_id: ファイルID
        user_id: リクエストユーザーID（オプション）
        group_id: リクエストグループID（オプション）
    """
    try:
        print(f"🔍 ファイル配信リクエスト: {file_id}")
        print(f"👤 アクセス制御: user_id={user_id}, group_id={group_id}")
        
        # ファイルを検索（アクセス制御付き）
        file_info = file_service.get_file_by_id(
            file_id=file_id,
            requester_user_id=user_id,
            requester_group_id=group_id
        )
        if not file_info:
            print(f"❌ ファイル情報が見つからないか、アクセス権限がありません: {file_id}")
            raise HTTPException(status_code=404, detail="File not found or access denied")
        
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

@router.get("/api/files")
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

@router.get("/api/files/{file_id}")
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

@router.get("/api/memoir/edit/{session_id}")
async def get_memoir_edit_data(session_id: str):
    """編集データ取得API"""
    try:
        session = quick_memoir_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "data": {
                "title": session.data.title,
                "subtitle": session.data.subtitle,
                "author": session.data.author,
                "cover_image_url": session.data.cover_image_url,
                "profile": session.data.profile,
                "timeline": session.data.timeline,
                "template": session.data.template
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f'Error getting memoir edit data: {e}')
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/memoir/save/{session_id}")
async def save_memoir_data(session_id: str, request: MemoirSaveRequest):
    """編集データ保存＆PDF再生成API"""
    try:
        # セッションを取得
        session = quick_memoir_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # データを更新
        success = quick_memoir_service.update_memoir_data(session_id, request.data)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update data")
        
        # PDF再生成
        pdf_result = await quick_memoir_service.generate_quick_pdf(session)
        
        # PDFファイルを保存
        file_metadata = file_service.save_file(
            pdf_result["pdf_buffer"],
            pdf_result["filename"],
            "application/pdf"
        )
        
        # PDFのURLを取得
        pdf_url = file_service.get_file_url(file_metadata['file_id'], settings.BASE_URL)
        edit_url = f"{settings.BASE_URL}/liff/edit.html?session_id={session_id}"
        
        # LINEにFlex Message（更新完了）を送信
        from app.services.line_service import send_memoir_updated_message
        send_memoir_updated_message(session.user_id, pdf_url, edit_url)
        
        return {
            "success": True,
            "pdf_url": pdf_url,
            "message": "PDFを更新しました"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f'Error saving memoir data: {e}')
        print(f'Full traceback:\n{error_trace}')
        raise HTTPException(status_code=500, detail=f"PDF生成エラー: {str(e)}")


@router.post("/api/memoir/generate-text")
async def generate_memoir_text(request: TextGenerationRequest):
    """LLM文章生成API"""
    try:
        from ..services.openai_service import generate_memoir_text
        
        generated_text = generate_memoir_text(request.type, request.data)
        
        return {
            "success": True,
            "generated_text": generated_text
        }
        
    except Exception as e:
        print(f'Error generating text: {e}')
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/memoir/edit-media/{session_id}")
async def get_media_memoir_edit_data(session_id: str):
    """メディアテンプレート編集データ取得API"""
    try:
        session = quick_memoir_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # メディアテンプレートスキーマを取得
        template = get_template("memoir_vertical")
        
        return {
            "session_id": session.session_id,
            "template_id": "memoir_vertical",
            "template_name": template.template_name if template else "自分史_縦書き",
            "title": session.data.title,
            "author": session.data.author,
            "cover_image_url": session.data.cover_image_url,
            "spread_image_url": session.spread_image_url,
            "single_image_url": session.single_image_url,
            "spread_text": session.spread_text,  # セッションから取得
            "single_title": session.single_title,  # セッションから取得
            "single_text": session.single_text  # セッションから取得
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f'Error getting media memoir edit data: {e}')
        print(f'Full traceback:\n{error_trace}')
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/memoir/save-media/{session_id}")
async def save_media_memoir_data(session_id: str, request: MediaMemoirSaveRequest):
    """メディアテンプレート編集データ保存＆完全版PDF再生成API"""
    try:
        # セッションを取得
        session = quick_memoir_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # 基本情報を更新
        session.data.title = request.title
        session.data.author = request.author
        
        # メディアテンプレート用のテキストを更新
        session.spread_text = request.spread_text
        session.single_title = request.single_title or "大切な一枚"
        session.single_text = request.single_text
        
        # 完全版PDFを再生成（カスタマイズされたテキストを使用）
        import asyncio
        
        # _prepare_media_template_dataをオーバーライド
        template_data = {
            "title": request.title,
            "pages": [
                # ページ1: タイトルページ（表紙）
                {
                    "page_type": "title",
                    "page_number": 1,
                    "data": {
                        "title": request.title,
                        "author": request.author,
                        "cover_image": session.data.cover_image_url
                    }
                },
                # ページ2-3: 見開き画像+縦書きテキスト（カスタマイズ版）
                {
                    "page_type": "spread_image_text",
                    "page_number": 2,
                    "data": {
                        "image": session.spread_image_url,
                        "story_title": "",  # タイトルは不要（格言のみ）
                        "story_text": request.spread_text
                    }
                },
                # ページ4: 単一ページ画像+テキスト（カスタマイズ版）
                {
                    "page_type": "single_image_text",
                    "page_number": 4,
                    "data": {
                        "image": session.single_image_url,
                        "section_title": request.single_title or "大切な一枚",
                        "description": request.single_text
                    }
                }
            ]
        }
        
        # 完全版PDF生成
        from pathlib import Path
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in request.title if c.isalnum() or c in (' ', '-', '_'))[:20]
        filename = f"memoir_vertical_{safe_title}_{timestamp}.pdf"
        
        output_dir = Path(settings.UPLOADS_DIR)
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / filename
        
        vivliostyle_options = {
            "size": "A4",
            "format": "pdf",
            "single_doc": True,
            "timeout": 90
        }
        
        from ..services.vivliostyle_service import vivliostyle_service
        await vivliostyle_service.generate_pdf(
            template_name="media/memoir-vertical",
            data=template_data,
            output_path=output_path,
            vivliostyle_options=vivliostyle_options
        )
        
        # PDFファイルを読み込み
        with open(output_path, "rb") as f:
            pdf_buffer = f.read()
        
        # PDFファイルを保存
        file_metadata = file_service.save_file(
            pdf_buffer,
            filename,
            "application/pdf"
        )
        
        # PDFのURLを取得
        pdf_url = file_service.get_file_url(file_metadata['file_id'], settings.BASE_URL)
        edit_url = f"{settings.BASE_URL}/liff/edit-media.html?session_id={session_id}"
        
        # FlexMessageを送信（更新完了版）
        from ..services.line_service import send_memoir_updated_message
        try:
            send_memoir_updated_message(
                user_id=session.user_id,
                pdf_url=pdf_url,
                edit_url=edit_url
            )
        except Exception as flex_error:
            # FlexMessage失敗時はテキストメッセージにフォールバック
            print(f"Flex Message送信失敗: {flex_error}, テキストメッセージにフォールバック")
            complete_message = (
                f"✨ 編集した自分史PDFが完成しました！\n\n"
                f"📄 PDF: {pdf_url}\n"
                f"✏️ さらに編集: {edit_url}\n\n"
                f"ファイル名: {filename}\n"
                f"サイズ: {len(pdf_buffer):,} bytes"
            )
            send_push_message(session.user_id, complete_message)
        
        return {
            "success": True,
            "pdf_url": pdf_url,
            "message": "PDFを更新しました"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f'Error saving media memoir data: {e}')
        print(f'Full traceback:\n{error_trace}')
        raise HTTPException(status_code=500, detail=f"PDF生成エラー: {str(e)}")


@router.get("/")
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
            "api_file_info": "GET /api/files/{file_id}",
            "memoir_edit": "GET /api/memoir/edit/{session_id}",
            "memoir_save": "POST /api/memoir/save/{session_id}",
            "memoir_edit_media": "GET /api/memoir/edit-media/{session_id}",
            "memoir_save_media": "POST /api/memoir/save-media/{session_id}",
            "memoir_generate_text": "POST /api/memoir/generate-text"
        }
    }

