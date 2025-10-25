"""
写真中心・対話ベース自分史作成サービス

ユーザーが複数の写真をアップロードし、それぞれの写真について対話形式で質問に答えることで、
AIが自動的にストーリーを生成し、美しい自分史PDFを作成します。
"""

import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from ..config import settings
from .vivliostyle_service import vivliostyle_service


@dataclass
class PhotoItem:
    """写真アイテム"""
    photo_id: str
    photo_url: str
    uploaded_at: datetime = field(default_factory=datetime.now)
    # 質問・回答
    current_question_index: int = 0
    answers: List[str] = field(default_factory=list)
    # 生成されたストーリー
    generated_story: Optional[str] = None
    story_approved: bool = False
    # メタデータ
    estimated_date: Optional[str] = None
    estimated_location: Optional[str] = None


@dataclass
class PhotoMemoirSession:
    """写真自分史セッション"""
    session_id: str
    user_id: str
    state: str  # "collecting_photos" | "questioning" | "story_generated" | "completed"
    photos: List[PhotoItem] = field(default_factory=list)
    current_photo_index: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def get_current_photo(self) -> Optional[PhotoItem]:
        """現在処理中の写真を取得"""
        if 0 <= self.current_photo_index < len(self.photos):
            return self.photos[self.current_photo_index]
        return None
    
    def has_more_photos(self) -> bool:
        """未処理の写真が残っているか"""
        return self.current_photo_index < len(self.photos)
    
    def next_photo(self) -> bool:
        """次の写真に進む"""
        if self.current_photo_index < len(self.photos) - 1:
            self.current_photo_index += 1
            self.updated_at = datetime.now()
            return True
        return False
    
    def get_progress(self) -> Tuple[int, int]:
        """進捗を取得 (現在, 総数)"""
        return (self.current_photo_index + 1, len(self.photos))


class PhotoMemoirService:
    """写真中心自分史作成サービス"""
    
    # 固定質問リスト（Phase 1では固定質問を使用）
    DEFAULT_QUESTIONS = [
        "いつ頃の写真ですか？（例：2015年春、10年前、子供の頃）",
        "どこで撮った写真ですか？",
        "この時の思い出やエピソードを教えてください",
    ]
    
    def __init__(self):
        self.sessions: Dict[str, PhotoMemoirSession] = {}
    
    
    def start_photo_memoir(self, user_id: str) -> Tuple[PhotoMemoirSession, str]:
        """写真自分史作成を開始"""
        session_id = f"photo_{uuid.uuid4().hex[:12]}"
        session = PhotoMemoirSession(
            session_id=session_id,
            user_id=user_id,
            state="collecting_photos"
        )
        self.sessions[session_id] = session
        
        response_message = (
            "📸 写真で自分史を作りましょう！\n\n"
            "まず、思い出の写真を送ってください。\n"
            "複数枚送ってもOKです✨\n\n"
            "送り終わったら「完了」と送信してください。"
        )
        
        return session, response_message
    
    def get_session_by_user(self, user_id: str) -> Optional[PhotoMemoirSession]:
        """ユーザーIDから最新のアクティブセッションを取得"""
        active_sessions = [
            s for s in self.sessions.values()
            if s.user_id == user_id and s.state in ["collecting_photos", "questioning", "story_generated"]
        ]
        if active_sessions:
            return sorted(active_sessions, key=lambda s: s.updated_at, reverse=True)[0]
        return None
    
    def get_session(self, session_id: str) -> Optional[PhotoMemoirSession]:
        """セッションIDからセッションを取得"""
        return self.sessions.get(session_id)
    
    def add_photo(self, session: PhotoMemoirSession, photo_url: str) -> str:
        """写真を追加"""
        photo_id = f"photo_{uuid.uuid4().hex[:8]}"
        photo = PhotoItem(
            photo_id=photo_id,
            photo_url=photo_url
        )
        session.photos.append(photo)
        session.updated_at = datetime.now()
        
        count = len(session.photos)
        response_message = f"写真{count}枚目を受け取りました📸\n他にも写真があれば送ってください。\n完了したら「完了」と送信してください。"
        
        return response_message
    
    def finish_photo_collection(self, session: PhotoMemoirSession) -> Tuple[bool, str]:
        """写真収集を完了し、質問フェーズに移行"""
        if len(session.photos) == 0:
            return False, "写真が1枚も登録されていません。まず写真を送ってください📸"
        
        session.state = "questioning"
        session.current_photo_index = 0
        session.updated_at = datetime.now()
        
        photo_count = len(session.photos)
        response_message = (
            f"✨ 写真を{photo_count}枚受け取りました！\n\n"
            f"これから各写真について質問しますので、\n"
            f"答えてください（テキストでも音声でもOK🎤）\n\n"
            f"それでは、1枚目の写真について教えてください！"
        )
        
        return True, response_message
    
    def get_current_question(self, session: PhotoMemoirSession) -> Optional[Tuple[str, PhotoItem, int]]:
        """現在の質問を取得
        
        Returns:
            (質問文, 写真情報, 質問番号) or None
        """
        photo = session.get_current_photo()
        if not photo:
            return None
        
        if photo.current_question_index >= len(self.DEFAULT_QUESTIONS):
            return None
        
        question = self.DEFAULT_QUESTIONS[photo.current_question_index]
        return (question, photo, photo.current_question_index + 1)
    
    def process_answer(self, session: PhotoMemoirSession, answer: str) -> Tuple[str, bool]:
        """回答を処理
        
        Returns:
            (レスポンスメッセージ, 次のアクションが必要か)
        """
        photo = session.get_current_photo()
        if not photo:
            return "エラー: 現在処理中の写真が見つかりません", False
        
        # 回答を保存
        photo.answers.append(answer)
        photo.current_question_index += 1
        session.updated_at = datetime.now()
        
        # まだ質問が残っている場合
        if photo.current_question_index < len(self.DEFAULT_QUESTIONS):
            next_question = self.DEFAULT_QUESTIONS[photo.current_question_index]
            response = f"ありがとうございます！\n\n次の質問です：\n{next_question}"
            return response, False
        
        # この写真の質問が終了
        current, total = session.get_progress()
        response = (
            f"✨ {current}枚目の写真の回答が完了しました！\n"
            f"AIがストーリーを生成しています...⏳"
        )
        
        # ストーリー生成が必要
        return response, True
    
    def generate_story_for_photo(self, photo: PhotoItem) -> str:
        """写真に対するストーリーを生成
        
        Args:
            photo: 写真情報（回答含む）
        
        Returns:
            生成されたストーリー
        """
        from .openai_service import openai_service
        
        # 回答を整形
        answers_text = "\n".join([f"- {answer}" for answer in photo.answers])
        
        prompt = f"""
以下は、ユーザーが自分の思い出の写真について答えた内容です。
これを100〜200文字程度の、温かみのある自分史のストーリーにまとめてください。

ユーザーの回答:
{answers_text}

要件:
- 100〜200文字程度
- 情緒的で温かみのある文章
- 時期・場所・出来事を自然に盛り込む
- 読者が情景を想像できる表現
- 過去形で記述
- 「。」で文を区切る

ストーリーのみを出力してください（説明や前置きは不要です）。
"""
        
        story = openai_service.get_chatgpt_response(prompt.strip())
        return story.strip()
    
    def get_story_approval_message(self, session: PhotoMemoirSession, story: str) -> str:
        """ストーリー承認メッセージを生成"""
        current, total = session.get_progress()
        
        message = (
            f"【生成されたストーリー】\n\n"
            f"{story}\n\n"
            f"このままでOKですか？\n"
            f"👍 いいね（次へ）\n"
            f"🔄 再生成\n"
            f"✏️ 修正（テキストで修正内容を送信）"
        )
        
        return message
    
    def handle_story_approval(self, session: PhotoMemoirSession, response: str) -> Tuple[str, bool]:
        """ストーリー承認の処理
        
        Returns:
            (レスポンスメッセージ, 次の写真に進むか)
        """
        photo = session.get_current_photo()
        if not photo or not photo.generated_story:
            return "エラー: ストーリーが見つかりません", False
        
        # 絵文字または明確な承認ワード
        if "👍" in response or "いいね" in response or "OK" in response.upper() or "次" in response:
            # 承認
            photo.story_approved = True
            session.updated_at = datetime.now()
            
            # 次の写真に進む
            if session.next_photo():
                current, total = session.get_progress()
                next_message = (
                    f"✨ 次の写真です（{current}/{total}枚目）\n\n"
                    f"{self.DEFAULT_QUESTIONS[0]}"
                )
                return next_message, True
            else:
                # 全写真完了
                session.state = "completed"
                return "すべての写真のストーリーが完成しました！\nPDFを生成しています...⏳", True
        
        elif "🔄" in response or "再生成" in response:
            # 再生成
            return "ストーリーを再生成しています...⏳", True
        
        else:
            # 修正内容として処理
            # 簡易実装: 修正内容を追加の回答として扱い、再生成
            photo.answers.append(f"[修正要望] {response}")
            return "修正内容を反映してストーリーを再生成しています...⏳", True
    
    def generate_pdf(self, session: PhotoMemoirSession) -> Dict[str, Any]:
        """写真自分史のPDFを生成
        
        Returns:
            PDF生成結果
        """
        try:
            # テンプレートデータを準備
            template_data = self._prepare_template_data(session)
            
            # ファイル名を生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"photo_memoir_{session.user_id[:8]}_{timestamp}.pdf"
            
            # 出力PDFパス
            output_dir = Path(settings.UPLOADS_DIR)
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / filename
            
            # Vivliostyleオプション
            vivliostyle_options = {
                "size": "A4",
                "format": "pdf",
                "single_doc": True,
                "timeout": 120  # 写真が多い場合は時間がかかる
            }
            
            # Vivliostyleで非同期PDF生成（同期的に実行）
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    vivliostyle_service.generate_pdf(
                        template_name="photo-memoir",
                        data=template_data,
                        output_path=output_path,
                        vivliostyle_options=vivliostyle_options
                    )
                )
            finally:
                loop.close()
            
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
    
    def _prepare_template_data(self, session: PhotoMemoirSession) -> Dict[str, Any]:
        """Vivliostyleテンプレート用にデータを整形"""
        pages = []
        
        for idx, photo in enumerate(session.photos, 1):
            page = {
                "page_number": idx,
                "image": photo.photo_url,
                "story": photo.generated_story or "（ストーリー未生成）",
                "date": photo.estimated_date or "",
                "location": photo.estimated_location or "",
            }
            pages.append(page)
        
        template_data = {
            "title": "思い出のアルバム",
            "author": "あなた",
            "date": datetime.now().strftime("%Y年%m月"),
            "photo_count": len(session.photos),
            "pages": pages
        }
        
        return template_data
    
    def cancel_session(self, session_id: str) -> bool:
        """セッションをキャンセル"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False


# グローバルインスタンス
photo_memoir_service = PhotoMemoirService()

