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
    state: str  # "waiting_title" | "waiting_cover" | "editing" | "completed"
    data: QuickMemoirData = None
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
            if s.user_id == user_id and s.state in ["waiting_title", "waiting_cover"]
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
        session.state = "editing"
        session.updated_at = datetime.now()
        
        response_message = "カバー写真を受け取りました！\nPDFを生成中です...⏳"
        
        return True, response_message
    
    async def generate_quick_pdf(
        self, 
        session: QuickMemoirSession,
        vivliostyle_options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """簡易PDFを生成（Vivliostyle使用）
        
        Args:
            session: 自分史セッション
            vivliostyle_options: Vivliostyle CLIオプション（省略可）
                例: {"size": "A4", "crop_marks": True, "bleed": "3mm"}
        
        Returns:
            PDF生成結果
        """
        try:
            # テンプレートデータを準備
            template_data = self._prepare_template_data(session.data)
            
            # ファイル名を生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = "".join(c for c in session.data.title if c.isalnum() or c in (' ', '-', '_'))[:20]
            filename = f"memoir_{safe_title}_{timestamp}.pdf"
            
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
                    "timeout": 90  # 自分史は画像が多いので90秒に延長
                }
            
            # Vivliostyleで非同期PDF生成（awaitで実行）
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
        """Vivliostyleテンプレート用にデータを整形"""
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
        
        # デバッグ: テンプレートデータ生成時の情報
        print(f"[DEBUG] _prepare_template_data:")
        print(f"  cover_image: {data.cover_image_url}")
        print(f"  timeline count: {len(data.timeline)}")
        
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
                print(f"[DEBUG]   年 {item.get('year')} に画像: {item['image']}")
            else:
                print(f"[DEBUG]   年 {item.get('year')} に画像なし")
            
            template_data["timeline"].append(timeline_item)
        
        return template_data
    
    def cancel_session(self, session_id: str) -> bool:
        """セッションをキャンセル"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False


# グローバルインスタンス
quick_memoir_service = QuickMemoirService()

