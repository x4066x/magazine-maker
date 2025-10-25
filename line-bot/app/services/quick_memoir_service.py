"""
簡易自分史作成サービス
最小限の入力（タイトル + カバー写真）でPDFを生成し、後から編集可能にする
"""

import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from ..config import settings
from .vivliostyle_service import vivliostyle_service


@dataclass
class QuickMemoirData:
    """簡易自分史データ構造"""
    title: str
    subtitle: str = "〜これまでの道のり〜"
    author: str = "あなた"
    date: str = ""
    cover_image_url: Optional[str] = None
    profile: Dict[str, Any] = field(default_factory=lambda: {
        "description": "",
        "birthDate": "",
        "birthPlace": "",
        "occupation": "",
        "hobbies": []
    })
    timeline: list = field(default_factory=list)
    template: str = "modern-vertical-cover"


@dataclass
class QuickMemoirSession:
    """簡易自分史作成セッション"""
    session_id: str
    user_id: str
    state: str  # "waiting_title" | "waiting_cover" | "waiting_spread_image" | "waiting_single_image" | "editing" | "completed"
    data: QuickMemoirData = None
    spread_image_url: Optional[str] = None  # 見開きページ用画像
    single_image_url: Optional[str] = None  # 単一ページ用画像
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if self.data is None:
            self.data = QuickMemoirData(title="")


class QuickMemoirService:
    """簡易自分史作成サービス"""
    
    def __init__(self):
        self.sessions: Dict[str, QuickMemoirSession] = {}
    
    def is_quick_create_request(self, message: str) -> bool:
        """簡易作成リクエストかどうかを判定"""
        trigger_keywords = ['作る', '作成', 'つくる', 'create', '自分史']
        return any(keyword in message.lower() for keyword in trigger_keywords)
    
    def start_quick_create(self, user_id: str) -> tuple[QuickMemoirSession, str]:
        """簡易作成を開始"""
        session_id = f"quick_{uuid.uuid4().hex[:12]}"
        session = QuickMemoirSession(
            session_id=session_id,
            user_id=user_id,
            state="waiting_title"
        )
        self.sessions[session_id] = session
        
        response_message = (
            "✨ 自分史を作成しましょう！\n\n"
            "まず、タイトルを教えてください。\n"
            "（例：私の人生物語、母の思い出、など）"
        )
        
        return session, response_message
    
    def get_session_by_user(self, user_id: str) -> Optional[QuickMemoirSession]:
        """ユーザーIDから最新のアクティブセッションを取得"""
        active_sessions = [
            s for s in self.sessions.values()
            if s.user_id == user_id and s.state in ["waiting_title", "waiting_cover", "waiting_spread_image", "waiting_single_image"]
        ]
        if active_sessions:
            # 最新のセッションを返す
            return sorted(active_sessions, key=lambda s: s.updated_at, reverse=True)[0]
        return None
    
    def get_session(self, session_id: str) -> Optional[QuickMemoirSession]:
        """セッションIDからセッションを取得"""
        return self.sessions.get(session_id)
    
    def process_title(self, session: QuickMemoirSession, title: str) -> str:
        """タイトルを処理"""
        session.data.title = title
        session.state = "waiting_cover"
        session.updated_at = datetime.now()
        
        response_message = (
            f"タイトル：「{title}」\n\n"
            "次に、カバー写真を送ってください。\n"
            "📸 写真を選択してアップロードしてください。"
        )
        
        return response_message
    
    def process_cover_image(self, session: QuickMemoirSession, image_url: str) -> tuple[bool, str]:
        """カバー画像を処理"""
        session.data.cover_image_url = image_url
        session.data.date = datetime.now().strftime("%Y年%m月")
        session.state = "waiting_spread_image"  # 次は見開き画像を待つ
        session.updated_at = datetime.now()
        
        response_message = "カバー写真を受け取りました！\n表紙PDFを生成中です...⏳"
        
        return True, response_message
    
    def process_spread_image(self, session: QuickMemoirSession, image_url: str) -> tuple[bool, str]:
        """見開きページ用画像を処理"""
        session.spread_image_url = image_url
        session.state = "waiting_single_image"
        session.updated_at = datetime.now()
        
        response_message = (
            "見開きページ用の写真を受け取りました！📸\n\n"
            "最後に、単一ページ用の写真を送ってください。\n"
            "（例：思い出の1枚、学生時代の写真など）"
        )
        
        return True, response_message
    
    def process_single_image(self, session: QuickMemoirSession, image_url: str) -> tuple[bool, str]:
        """単一ページ用画像を処理"""
        session.single_image_url = image_url
        session.state = "editing"
        session.updated_at = datetime.now()
        
        response_message = "単一ページ用の写真を受け取りました！\n完全版PDFを生成中です...⏳"
        
        return True, response_message
    
    async def generate_quick_pdf(
        self, 
        session: QuickMemoirSession,
        vivliostyle_options: Dict[str, Any] = None,
        full_version: bool = False
    ) -> Dict[str, Any]:
        """PDFを生成（Vivliostyle使用）
        
        Args:
            session: 自分史セッション
            vivliostyle_options: Vivliostyle CLIオプション（省略可）
            full_version: True=完全版（メディアテンプレート）、False=表紙のみ
        
        Returns:
            PDF生成結果
        """
        try:
            # ファイル名を生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = "".join(c for c in session.data.title if c.isalnum() or c in (' ', '-', '_'))[:20]
            
            # 出力PDFパス
            output_dir = Path(settings.UPLOADS_DIR)
            output_dir.mkdir(exist_ok=True)
            
            # デフォルトのVivliostyleオプション
            if vivliostyle_options is None:
                vivliostyle_options = {
                    "size": "A4",
                    "format": "pdf",
                    "single_doc": True,
                    "timeout": 90
                }
            
            if full_version and session.spread_image_url and session.single_image_url:
                # 完全版: メディアテンプレート形式
                template_data = self._prepare_media_template_data(session)
                filename = f"memoir_vertical_{safe_title}_{timestamp}.pdf"
                output_path = output_dir / filename
                
                await vivliostyle_service.generate_pdf(
                    template_name="media/memoir-vertical",
                    data=template_data,
                    output_path=output_path,
                    vivliostyle_options=vivliostyle_options
                )
            else:
                # 表紙のみ: 簡易版
                template_data = self._prepare_template_data(session.data)
                filename = f"memoir_{safe_title}_{timestamp}.pdf"
                output_path = output_dir / filename
                
                await vivliostyle_service.generate_pdf(
                    template_name="memoir",
                    data=template_data,
                    output_path=output_path,
                    vivliostyle_options=vivliostyle_options
                )
            
            # PDFファイルを読み込み
            with open(output_path, "rb") as f:
                pdf_buffer = f.read()
            
            return {
                "success": True,
                "pdf_buffer": pdf_buffer,
                "filename": filename,
                "size": len(pdf_buffer),
                "path": str(output_path)
            }
            
        except Exception as e:
            raise Exception(f"PDF生成に失敗しました: {str(e)}")
    
    def update_memoir_data(self, session_id: str, data: Dict[str, Any]) -> bool:
        """編集画面からのデータを更新
        
        Note: 画像URLはセッションデータから保持されるため、編集データには含まれていなくてOK
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        # デバッグ: 更新前のセッションデータを出力
        print(f"[DEBUG] 更新前のセッションデータ:")
        print(f"  cover_image_url: {session.data.cover_image_url}")
        print(f"  timeline: {session.data.timeline}")
        
        # 編集可能な項目のみ更新
        if "title" in data:
            session.data.title = data["title"]
        if "subtitle" in data:
            session.data.subtitle = data["subtitle"]
        if "author" in data:
            session.data.author = data["author"]
        if "profile" in data:
            session.data.profile.update(data["profile"])
        
        # 年表データを更新（画像URLは元のセッションデータから保持）
        if "timeline" in data:
            # 既存の年表データから画像URLのマップを作成
            existing_images = {}
            for item in session.data.timeline:
                year = item.get("year")
                if year and "image" in item:
                    existing_images[year] = item["image"]
            
            print(f"[DEBUG] 既存の画像マップ: {existing_images}")
            
            # 新しい年表データに既存の画像URLをマージ
            new_timeline = []
            for item in data["timeline"]:
                new_item = item.copy()
                year = item.get("year")
                
                # 既存の画像URLがあれば保持（新しいデータに含まれていなくても）
                if year in existing_images and "image" not in new_item:
                    new_item["image"] = existing_images[year]
                    print(f"[DEBUG] 年 {year} に画像URLをマージ: {existing_images[year]}")
                
                new_timeline.append(new_item)
            
            session.data.timeline = new_timeline
        
        if "template" in data:
            session.data.template = data["template"]
        
        # デバッグ: 更新後のセッションデータを出力
        print(f"[DEBUG] 更新後のセッションデータ:")
        print(f"  cover_image_url: {session.data.cover_image_url}")
        print(f"  timeline: {session.data.timeline}")
        
        session.updated_at = datetime.now()
        return True
    
    def _prepare_template_data(self, data: QuickMemoirData) -> Dict[str, Any]:
        """Vivliostyleテンプレート用にデータを整形（表紙のみ）"""
        template_data = {
            "title": data.title,
            "subtitle": data.subtitle,
            "author": data.author,
            "date": data.date or datetime.now().strftime("%Y年%m月"),
            "cover_image": data.cover_image_url,
            "profile": {
                "name": data.author,
                "birthDate": data.profile.get("birthDate", ""),
                "birthPlace": data.profile.get("birthPlace", ""),
                "occupation": data.profile.get("occupation", ""),
                "hobbies": data.profile.get("hobbies", []),
                "description": data.profile.get("description", "")
            },
            "timeline": []
        }
        
        # 年表データを整形
        for item in data.timeline:
            timeline_item = {
                "year": item.get("year", 2000),
                "title": item.get("title", ""),
                "description": item.get("description", ""),
                "tags": item.get("tags", [])
            }
            
            # 画像がある場合は追加
            if "image" in item:
                timeline_item["image"] = item["image"]
            
            template_data["timeline"].append(timeline_item)
        
        return template_data
    
    def _prepare_media_template_data(self, session: QuickMemoirSession) -> Dict[str, Any]:
        """メディアテンプレート用にデータを整形（完全版）"""
        return {
            "title": session.data.title,
            "pages": [
                # ページ1: タイトルページ（表紙）
                {
                    "page_type": "title",
                    "page_number": 1,
                    "data": {
                        "title": session.data.title,
                        "author": session.data.author,
                        "cover_image": session.data.cover_image_url
                    }
                },
                # ページ2-3: 見開き画像+縦書きテキスト
                {
                    "page_type": "spread_image_text",
                    "page_number": 2,
                    "data": {
                        "image": session.spread_image_url,
                        "story_title": "思い出のひととき",
                        "story_text": (
                            "この写真には、大切な思い出が詰まっています。時が経つにつれて、記憶は少しずつ色褪せていくかもしれません。"
                            "しかし、この一枚の写真が、あの日の感動や喜びを鮮やかに蘇らせてくれます。"
                            "人生の旅路において、このような瞬間を大切に残しておくことは、とても意味のあることです。"
                            "写真を見るたびに、当時の気持ちや周囲の雰囲気が心に蘇ってきます。"
                            "それは単なる記録ではなく、心の財産として、これからも大切に保管していきたいと思います。"
                        )
                    }
                },
                # ページ4: 単一ページ画像+テキスト
                {
                    "page_type": "single_image_text",
                    "page_number": 4,
                    "data": {
                        "image": session.single_image_url,
                        "section_title": "大切な一枚",
                        "description": (
                            "この写真は、人生の中で特別な意味を持つ一枚です。"
                            "何気ない日常の中にも、かけがえのない瞬間が隠れています。"
                            "写真として残すことで、その瞬間は永遠に私たちの心に刻まれます。"
                        )
                    }
                }
            ]
        }
    
    def cancel_session(self, session_id: str) -> bool:
        """セッションをキャンセル"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False


# グローバルインスタンス
quick_memoir_service = QuickMemoirService()

