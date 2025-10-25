import requests
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from ..config import settings

@dataclass
class MemoirData:
    """自分史データ構造"""
    title: str
    subtitle: str = "〜これまでの道のり〜"
    author: str = ""
    date: str = ""
    profile: Dict[str, Any] = None
    timeline: List[Dict[str, Any]] = None
    chapters: List[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.profile is None:
            self.profile = {}
        if self.timeline is None:
            self.timeline = []
        if self.chapters is None:
            self.chapters = []
        if self.metadata is None:
            self.metadata = {}

@dataclass
class MemoirSession:
    """自分史作成セッション"""
    user_id: str
    state: str = "idle"  # idle, collecting_profile, collecting_timeline, collecting_images, confirming, generating
    data: MemoirData = None
    current_step: int = 0
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = MemoirData(title="私の人生の歩み")
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

class MemoirService:
    """自分史作成サービス"""
    
    def __init__(self):
        self.sessions: Dict[str, MemoirSession] = {}
    
    
    def get_or_create_session(self, user_id: str) -> MemoirSession:
        """ユーザーセッションを取得または作成"""
        if user_id not in self.sessions:
            self.sessions[user_id] = MemoirSession(user_id=user_id)
        return self.sessions[user_id]
    
    def cancel_session(self, user_id: str) -> None:
        """セッションをキャンセル"""
        if user_id in self.sessions:
            del self.sessions[user_id]
    
    def process_message(self, user_id: str, message: str) -> str:
        """メッセージを処理して応答を生成"""
        session = self.get_or_create_session(user_id)
        session.updated_at = datetime.now()
        
        # キャンセル処理
        if message.lower() in ['キャンセル', 'cancel', 'やめる']:
            self.cancel_session(user_id)
            return "自分史作成をキャンセルしました。通常のチャットモードに戻ります。"
        
        # ヘルプ表示
        if message.lower() in ['ヘルプ', 'help', '?', '？']:
            return self._show_help(session)
        
        # 状態に応じた処理
        if session.state == "idle":
            return self._start_profile_collection(session)
        elif session.state == "collecting_profile":
            return self._process_profile_input(session, message)
        elif session.state == "collecting_timeline":
            return self._process_timeline_input(session, message)
        elif session.state == "confirming":
            return self._process_confirmation(session, message)
        elif session.state == "generating":
            return "PDFを生成中です。しばらくお待ちください..."
        
        return "エラーが発生しました。もう一度「自分史作成」と入力してください。"
    
    def _show_help(self, session: MemoirSession) -> str:
        """ヘルプメッセージを表示"""
        if session.state == "idle":
            return "自分史作成を開始するには「自分史作成」と入力してください。"
        elif session.state == "collecting_profile":
            return "基本情報を入力中です。\n現在の質問に答えてください。\nキャンセルする場合は「キャンセル」と入力してください。"
        elif session.state == "collecting_timeline":
            return "年表を作成中です。\n出来事を年付きで教えてください。（例：1991年：小学校入学）\n完了する場合は「完了」と入力してください。\nキャンセルする場合は「キャンセル」と入力してください。"
        elif session.state == "confirming":
            return "情報の確認中です。\nPDFを生成する場合は「はい」、キャンセルする場合は「いいえ」と入力してください。"
        elif session.state == "generating":
            return "PDFを生成中です。しばらくお待ちください..."
        else:
            return "エラーが発生しました。もう一度「自分史作成」と入力してください。"
    
    def _start_profile_collection(self, session: MemoirSession) -> str:
        """プロフィール収集を開始"""
        session.state = "collecting_profile"
        session.current_step = 0
        return (
            "自分史の作成を開始します！まずは基本情報を教えてください。\n"
            "お名前を教えてください。\n\n"
            "💡 ヘルプが必要な場合は「ヘルプ」と入力してください。"
        )
    
    def _process_profile_input(self, session: MemoirSession, message: str) -> str:
        """プロフィール入力処理"""
        steps = [
            ("name", "生年月日を教えてください。\n（例：1985年3月15日）"),
            ("birthDate", "出身地を教えてください。"),
            ("birthPlace", "現在の職業を教えてください。"),
            ("occupation", "趣味があれば教えてください。（複数の場合はカンマ区切りで）"),
            ("hobbies", "自己紹介を一言で教えてください。")
        ]
        
        if session.current_step >= len(steps):
            return self._start_timeline_collection(session)
        
        field, next_prompt = steps[session.current_step]
        
        # データを保存
        if field == "name":
            session.data.author = message
            session.data.profile["name"] = message
        elif field == "birthDate":
            session.data.profile["birthDate"] = message
        elif field == "birthPlace":
            session.data.profile["birthPlace"] = message
        elif field == "occupation":
            session.data.profile["occupation"] = message
        elif field == "hobbies":
            hobbies = [h.strip() for h in message.split(',')]
            session.data.profile["hobbies"] = hobbies
        elif field == "description":
            session.data.profile["description"] = message
        
        session.current_step += 1
        
        if session.current_step >= len(steps):
            return self._start_timeline_collection(session)
        
        return next_prompt + "\n\n💡 ヘルプが必要な場合は「ヘルプ」と入力してください。"
    
    def _start_timeline_collection(self, session: MemoirSession) -> str:
        """年表収集を開始"""
        session.state = "collecting_timeline"
        session.current_step = 0
        
        # 生年月日から開始年を設定
        birth_date = session.data.profile.get("birthDate", "")
        start_year = self._extract_year(birth_date) or 1985
        
        session.data.profile["start_year"] = start_year
        
        return (
            "基本情報の収集が完了しました！\n"
            "次は人生の重要な出来事を年別に教えてください。\n"
            f"まず、{start_year}年の出来事を教えてください。\n\n"
            "💡 ヘルプが必要な場合は「ヘルプ」と入力してください。"
        )
    
    def _process_timeline_input(self, session: MemoirSession, message: str) -> str:
        """年表入力処理"""
        if message.lower() in ['完了', 'finish', '終了']:
            return self._show_confirmation(session)
        
        # 最新の年表項目を取得
        if not session.data.timeline:
            # 最初の項目の場合
            year = session.data.profile.get("start_year", 1985)
            title = message
        else:
            latest_item = session.data.timeline[-1]
            
            # 説明が未入力の場合、説明として扱う
            if not latest_item.get("description"):
                latest_item["description"] = message
                return f"{latest_item['year']}年：{latest_item['title']}\n説明を追加しました。\n次の出来事を教えてください。（例：1991年：小学校入学）\n\n💡 ヘルプが必要な場合は「ヘルプ」と入力してください。"
            
            # 新しい項目として処理
            # 年とタイトルを分離
            parts = message.split('：', 1)
            if len(parts) == 2:
                year_str, title = parts
                year = self._extract_year(year_str)
            else:
                # 年が含まれていない場合、前の年から推定
                prev_year = latest_item["year"]
                year = prev_year + 1
                title = message
        
        if not year:
            return "年を教えてください。（例：1991年：小学校入学）\n\n💡 ヘルプが必要な場合は「ヘルプ」と入力してください。"
        
        # 年表項目を追加
        timeline_item = {
            "year": year,
            "title": title,
            "description": "",
            "tags": []
        }
        
        session.data.timeline.append(timeline_item)
        
        return f"{year}年：{title}\nこの出来事について詳しく教えてください。（例：どのような気持ちでしたか？何が印象的でしたか？）\n\n💡 ヘルプが必要な場合は「ヘルプ」と入力してください。"
    
    def _show_confirmation(self, session: MemoirSession) -> str:
        """確認画面を表示"""
        session.state = "confirming"
        
        # データを整形
        profile = session.data.profile
        timeline = session.data.timeline
        
        confirmation_text = "収集した情報を確認します：\n\n"
        confirmation_text += f"名前：{profile.get('name', '')}\n"
        confirmation_text += f"生年月日：{profile.get('birthDate', '')}\n"
        confirmation_text += f"出身地：{profile.get('birthPlace', '')}\n"
        confirmation_text += f"職業：{profile.get('occupation', '')}\n"
        
        hobbies = profile.get('hobbies', [])
        if hobbies:
            confirmation_text += f"趣味：{', '.join(hobbies)}\n"
        
        confirmation_text += "\n年表：\n"
        for item in timeline:
            confirmation_text += f"- {item['year']}年：{item['title']}\n"
        
        confirmation_text += "\nPDFを生成しますか？（はい/いいえ）"
        
        return confirmation_text
    
    def _process_confirmation(self, session: MemoirSession, message: str) -> str:
        """確認処理"""
        if message.lower() in ['はい', 'yes', '生成', 'ok']:
            session.state = "generating"
            return "PDFを生成中です...しばらくお待ちください。"
        elif message.lower() in ['いいえ', 'no', 'キャンセル']:
            self.cancel_session(session.user_id)
            return "自分史作成をキャンセルしました。"
        else:
            return "「はい」または「いいえ」で回答してください。"
    
    def _extract_year(self, text: str) -> Optional[int]:
        """テキストから年を抽出"""
        import re
        match = re.search(r'(\d{4})', text)
        if match:
            return int(match.group(1))
        return None
    
    def generate_memoir_pdf(self, user_id: str) -> Dict[str, Any]:
        """自分史PDFを生成"""
        session = self.get_or_create_session(user_id)
        
        if session.state != "generating":
            raise ValueError("セッションが生成状態ではありません")
        
        try:
            # auto-designer APIにデータを送信
            memoir_data = self._prepare_memoir_data(session.data)
            
            response = requests.post(
                f"{settings.AUTO_DESIGNER_URL}/v2/pdf",
                json={
                    "template": "memoir",
                    "data": memoir_data,
                    "options": {
                        "format": "A4",
                        "margin": "20mm 15mm 25mm 15mm"
                    }
                },
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            # レスポンスのContent-Typeを確認
            content_type = response.headers.get('Content-Type', '')
            
            if response.status_code != 200:
                # エラーレスポンスの場合（JSON形式）
                try:
                    error_data = response.json()
                    error_message = error_data.get('error', {}).get('message', 'Unknown error')
                    error_details = error_data.get('error', {}).get('details', '')
                    raise Exception(f"PDF生成エラー: {error_message} - {error_details}")
                except ValueError:
                    # JSONパースに失敗した場合
                    raise Exception(f"PDF生成エラー: {response.status_code} - {response.text}")
            
            # 成功時はPDFバッファを直接返す
            if 'application/pdf' not in content_type:
                raise Exception(f"予期しないContent-Type: {content_type}")
            
            # PDFデータを取得
            pdf_buffer = response.content
            
            # ファイル名を生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"memoir_{session.data.author}_{timestamp}.pdf"
            
            return {
                "success": True,
                "pdf_buffer": pdf_buffer,
                "filename": filename,
                "size": len(pdf_buffer)
            }
            
        except Exception as e:
            # セッションをリセット
            session.state = "idle"
            raise Exception(f"PDF生成に失敗しました: {str(e)}")
    
    def _prepare_memoir_data(self, data: MemoirData) -> Dict[str, Any]:
        """auto-designer API用にデータを整形"""
        memoir_data = {
            "title": data.title,
            "subtitle": data.subtitle,
            "author": data.author,
            "date": data.date or datetime.now().strftime("%Y年%m月"),
            "profile": {
                "name": data.profile.get("name", data.author),
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
            # descriptionが空の場合はデフォルトの説明を設定
            description = item.get("description", "")
            if not description or description.strip() == "":
                description = f"{item['year']}年に起こった重要な出来事です。"
            
            timeline_item = {
                "year": item["year"],
                "title": item["title"],
                "description": description,
                "tags": item.get("tags", [])
            }
            
            # 画像がある場合は追加
            if "image" in item:
                timeline_item["image"] = item["image"]
                timeline_item["imageCaption"] = item.get("imageCaption", "")
            
            memoir_data["timeline"].append(timeline_item)
        
        return memoir_data
    
    def add_image_to_timeline(self, user_id: str, image_url: str, caption: str = "") -> bool:
        """年表に画像を追加"""
        session = self.get_or_create_session(user_id)
        
        if session.state != "collecting_timeline" or not session.data.timeline:
            return False
        
        # 最新の年表項目に画像を追加
        latest_item = session.data.timeline[-1]
        latest_item["image"] = image_url
        latest_item["imageCaption"] = caption
        
        return True

# グローバルインスタンス
memoir_service = MemoirService()

