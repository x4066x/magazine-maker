"""
メディアテンプレート駆動の自分史作成サービス

テンプレートスキーマに基づいて、ユーザーから情報を収集し、
構造化されたPDFを生成します。
"""

import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass, field
from ..config import settings
from .media_template_schema import (
    MediaTemplateSchema, 
    PageSchema, 
    PageType,
    get_template
)
from .vivliostyle_service import vivliostyle_service


@dataclass
class PageData:
    """ページデータ"""
    page_id: str  # ページID
    page_type: str  # ページタイプ（PageType.value）
    page_number: int  # ページ番号
    data: Dict[str, Any] = field(default_factory=dict)  # ページのデータ


@dataclass
class MediaMemoirSession:
    """メディア自分史セッション"""
    session_id: str
    user_id: str
    template_id: str  # 使用するテンプレートID
    state: str  # "collecting" | "editing" | "completed"
    current_field_index: int = 0  # 現在収集中のフィールドインデックス
    pages: List[PageData] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    # 所有者情報（アクセス制御用）
    owner_type: str = "user"  # "user" または "group"
    owner_id: Optional[str] = None  # user_id または group_id
    
    def get_page_by_id(self, page_id: str) -> Optional[PageData]:
        """ページIDからページデータを取得"""
        for page in self.pages:
            if page.page_id == page_id:
                return page
        return None


class MediaMemoirService:
    """メディアテンプレート駆動の自分史作成サービス"""
    
    def __init__(self):
        self.sessions: Dict[str, MediaMemoirSession] = {}
    
    def start_media_memoir(
        self, 
        user_id: str, 
        template_id: str = "memoir_vertical",
        owner_type: str = "user",
        owner_id: Optional[str] = None
    ) -> Tuple[Optional[MediaMemoirSession], str]:
        """メディア自分史作成を開始
        
        Args:
            user_id: ユーザーID
            template_id: テンプレートID
            owner_type: 所有者タイプ ("user" または "group")
            owner_id: 所有者ID (指定しない場合はuser_idを使用)
        """
        
        # テンプレートを取得
        template = get_template(template_id)
        if not template:
            return None, f"テンプレート '{template_id}' が見つかりません。"
        
        # セッション作成
        session_id = f"media_{uuid.uuid4().hex[:12]}"
        session = MediaMemoirSession(
            session_id=session_id,
            user_id=user_id,
            template_id=template_id,
            state="collecting",
            owner_type=owner_type,
            owner_id=owner_id or user_id
        )
        
        # ページデータを初期化
        for page_schema in template.pages:
            page_data = PageData(
                page_id=page_schema.page_id,
                page_type=page_schema.page_type.value,
                page_number=page_schema.page_number,
                data={}
            )
            session.pages.append(page_data)
        
        self.sessions[session_id] = session
        
        # 最初のフィールド収集を開始
        response = self._get_next_field_prompt(session, template)
        
        return session, response
    
    def get_session_by_user(self, user_id: str) -> Optional[MediaMemoirSession]:
        """ユーザーIDから最新のアクティブセッションを取得"""
        active_sessions = [
            s for s in self.sessions.values()
            if s.user_id == user_id and s.state == "collecting"
        ]
        if active_sessions:
            return sorted(active_sessions, key=lambda s: s.updated_at, reverse=True)[0]
        return None
    
    def get_session(self, session_id: str) -> Optional[MediaMemoirSession]:
        """セッションIDからセッションを取得"""
        return self.sessions.get(session_id)
    
    def process_user_input(self, session: MediaMemoirSession, input_data: Any, input_type: str = "text") -> Tuple[bool, str]:
        """ユーザー入力を処理
        
        Args:
            session: セッション
            input_data: 入力データ（テキストまたは画像URL）
            input_type: 入力タイプ（"text" | "image"）
        
        Returns:
            (成功フラグ, レスポンスメッセージ)
        """
        template = get_template(session.template_id)
        if not template:
            return False, "テンプレートが見つかりません。"
        
        # 現在収集中のフィールドを取得
        current_field_info = self._get_current_field(session, template)
        if not current_field_info:
            return False, "すべてのフィールドが収集済みです。"
        
        page_schema, field_schema, page_data = current_field_info
        
        # フィールドタイプの検証
        if field_schema.field_type == "image" and input_type != "image":
            return False, f"📸 {field_schema.description}の写真を送ってください。"
        
        if field_schema.field_type == "text" and input_type != "text":
            return False, f"✍️ {field_schema.description}をテキストで入力してください。"
        
        # データを保存
        page_data.data[field_schema.field_name] = input_data
        session.current_field_index += 1
        session.updated_at = datetime.now()
        
        # 次のフィールドまたは完了メッセージ
        response = self._get_next_field_prompt(session, template)
        
        return True, response
    
    def _get_current_field(self, session: MediaMemoirSession, template: MediaTemplateSchema) -> Optional[Tuple[PageSchema, Any, PageData]]:
        """現在収集中のフィールド情報を取得
        
        Returns:
            (PageSchema, FieldSchema, PageData) or None
        """
        field_count = 0
        
        for page_schema in template.pages:
            page_data = session.get_page_by_id(page_schema.page_id)
            if not page_data:
                continue
            
            for field_schema in page_schema.fields:
                if field_count == session.current_field_index:
                    return (page_schema, field_schema, page_data)
                field_count += 1
        
        return None
    
    def _get_next_field_prompt(self, session: MediaMemoirSession, template: MediaTemplateSchema) -> str:
        """次のフィールドのプロンプトを生成"""
        current_field_info = self._get_current_field(session, template)
        
        if not current_field_info:
            # すべてのフィールドが収集完了
            session.state = "editing"
            return (
                "✨ すべての情報を受け取りました！\n"
                "PDFを生成しています...⏳"
            )
        
        page_schema, field_schema, page_data = current_field_info
        
        # プログレス計算
        total_fields = sum(len(p.fields) for p in template.pages)
        current_progress = session.current_field_index + 1
        
        # プロンプト生成
        prompt = f"【{current_progress}/{total_fields}】\n"
        prompt += f"📄 {page_schema.display_name}\n\n"
        
        if field_schema.field_type == "image":
            prompt += f"📸 {field_schema.description}\n"
            prompt += "写真を送ってください。"
        else:
            prompt += f"✍️ {field_schema.description}\n"
            if field_schema.placeholder:
                prompt += f"（{field_schema.placeholder}）"
        
        return prompt
    
    async def generate_pdf(
        self,
        session: MediaMemoirSession,
        vivliostyle_options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """PDFを生成
        
        Returns:
            PDF生成結果
        """
        try:
            template = get_template(session.template_id)
            if not template:
                raise Exception(f"テンプレート '{session.template_id}' が見つかりません。")
            
            # テンプレートデータを準備
            template_data = self._prepare_template_data(session, template)
            
            # ファイル名を生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{template.template_id}_{timestamp}.pdf"
            
            # 出力PDFパス
            output_dir = Path(settings.UPLOADS_DIR)
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / filename
            
            # デフォルトのVivliostyleオプション
            if vivliostyle_options is None:
                vivliostyle_options = {
                    "size": "A4",
                    "format": "pdf",
                    "single_doc": True,
                    "timeout": 90
                }
            
            # Vivliostyleで非同期PDF生成
            await vivliostyle_service.generate_pdf(
                template_name=f"media/{template.template_id}",
                data=template_data,
                output_path=output_path,
                vivliostyle_options=vivliostyle_options
            )
            
            # PDFファイルを読み込み
            with open(output_path, "rb") as f:
                pdf_buffer = f.read()
            
            session.state = "completed"
            session.updated_at = datetime.now()
            
            return {
                "success": True,
                "pdf_buffer": pdf_buffer,
                "filename": filename,
                "size": len(pdf_buffer),
                "path": str(output_path)
            }
            
        except Exception as e:
            raise Exception(f"PDF生成に失敗しました: {str(e)}")
    
    def _prepare_template_data(self, session: MediaMemoirSession, template: MediaTemplateSchema) -> Dict[str, Any]:
        """Vivliostyleテンプレート用にデータを整形"""
        
        # タイトルページからタイトルを取得
        title = "自分史"
        title_page = session.get_page_by_id("title_page")
        if title_page and "title" in title_page.data:
            title = title_page.data["title"]
        
        # ページデータを整形
        pages = []
        for page_data in session.pages:
            pages.append({
                "page_type": page_data.page_type,
                "page_number": page_data.page_number,
                "data": page_data.data
            })
        
        return {
            "title": title,
            "pages": pages
        }
    
    def update_page_data(self, session_id: str, page_id: str, data: Dict[str, Any]) -> bool:
        """ページデータを更新（編集画面から）"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        page_data = session.get_page_by_id(page_id)
        if not page_data:
            return False
        
        page_data.data.update(data)
        session.updated_at = datetime.now()
        
        return True
    
    def add_page(self, session_id: str, page_type: str, insert_after: str = None) -> bool:
        """ページを追加（将来的な機能）"""
        # TODO: 実装
        return False
    
    def delete_page(self, session_id: str, page_id: str) -> bool:
        """ページを削除（is_deletable=Trueの場合のみ）"""
        # TODO: 実装
        return False
    
    def cancel_session(self, session_id: str) -> bool:
        """セッションをキャンセル"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False


# グローバルインスタンス
media_memoir_service = MediaMemoirService()

