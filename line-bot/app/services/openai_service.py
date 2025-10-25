from openai import OpenAI
from typing import Dict, Any, Optional
from .file_service import file_service
from ..config import settings
import json

# OpenAI クライアント設定
openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_chatgpt_response(user_message: str) -> str:
    """ユーザーのメッセージをChatGPTに送信し、短文レスポンスを取得"""
    try:
        # ファイル生成コマンドのチェック
        if is_file_generation_request(user_message):
            return handle_file_generation_request(user_message)
        
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "あなたは親切なアシスタントです。日本語で簡潔に1〜2文で回答してください。長文は避けてください。"
                },
                {"role": "user", "content": user_message}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        response_text = completion.choices[0].message.content
        print(f'ChatGPT response: {response_text}')
        return response_text
        
    except Exception as e:
        print(f'Error calling ChatGPT API: {e}')
        return f"エラーが発生しました: {str(e)}"

def is_file_generation_request(message: str) -> bool:
    """ファイル生成リクエストかどうかを判定"""
    file_generation_keywords = [
        'レポート作成', 'report create', 'ファイル作成', 'create file',
        'テキスト生成', 'text generate', 'JSON生成', 'json generate'
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in file_generation_keywords)

def handle_file_generation_request(message: str) -> str:
    """ファイル生成リクエストを処理"""
    try:
        message_lower = message.lower()
        
        if 'レポート' in message_lower or 'report' in message_lower:
            return handle_report_generation(message)
        elif 'json' in message_lower:
            return handle_json_generation(message)
        else:
            return handle_text_file_generation(message)
            
    except Exception as e:
        print(f'Error handling file generation: {e}')
        return f"ファイル生成エラー: {str(e)}"

def handle_report_generation(message: str) -> str:
    """レポート生成を処理"""
    try:
        # レポートの内容を生成
        report_content = generate_report_content(message)
        
        # テキストファイルとして保存
        file_metadata = file_service.save_file(
            report_content.encode('utf-8'),
            f"generated_report_{message[:10]}.txt",
            "text/plain"
        )
        
        file_url = file_service.get_file_url(file_metadata['file_id'], settings.BASE_URL)
        
        return f"レポートを生成しました！\nファイルURL: {file_url}"
        
    except Exception as e:
        print(f'Error generating report: {e}')
        return f"レポート生成エラー: {str(e)}"

def generate_report_content(message: str) -> str:
    """レポート内容を生成"""
    try:
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "あなたは詳細なレポートを作成する専門家です。ユーザーのリクエストに基づいて、構造化されたレポートを日本語で作成してください。"
                },
                {"role": "user", "content": message}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        return completion.choices[0].message.content
        
    except Exception as e:
        print(f'Error generating report content: {e}')
        return f"レポート内容生成エラー: {str(e)}"

def handle_json_generation(message: str) -> str:
    """JSON生成を処理"""
    try:
        # JSON内容を生成
        json_content = generate_json_content(message)
        
        # JSONファイルとして保存
        file_metadata = file_service.save_file(
            json_content.encode('utf-8'),
            f"generated_data_{message[:10]}.json",
            "application/json"
        )
        
        file_url = file_service.get_file_url(file_metadata['file_id'], settings.BASE_URL)
        
        return f"JSONファイルを生成しました！\nファイルURL: {file_url}"
        
    except Exception as e:
        print(f'Error generating JSON: {e}')
        return f"JSON生成エラー: {str(e)}"

def generate_json_content(message: str) -> str:
    """JSON内容を生成"""
    try:
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "あなたはJSONデータを生成する専門家です。ユーザーのリクエストに基づいて、有効なJSONファイルを作成してください。レスポンスはJSONフォーマットのみにしてください。"
                },
                {"role": "user", "content": message}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        return completion.choices[0].message.content
        
    except Exception as e:
        print(f'Error generating JSON content: {e}')
        return '{"error": "JSON生成エラー"}'

def handle_text_file_generation(message: str) -> str:
    """テキストファイル生成を処理"""
    try:
        # テキスト内容を生成
        text_content = generate_text_content(message)
        
        # テキストファイルとして保存
        file_metadata = file_service.save_file(
            text_content.encode('utf-8'),
            f"generated_text_{message[:10]}.txt",
            "text/plain"
        )
        
        file_url = file_service.get_file_url(file_metadata['file_id'], settings.BASE_URL)
        
        return f"テキストファイルを生成しました！\nファイルURL: {file_url}"
        
    except Exception as e:
        print(f'Error generating text file: {e}')
        return f"テキストファイル生成エラー: {str(e)}"

def generate_text_content(message: str) -> str:
    """テキスト内容を生成"""
    try:
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "あなたは詳細なテキストコンテンツを作成する専門家です。ユーザーのリクエストに基づいて、詳細で有用なテキストを日本語で作成してください。"
                },
                {"role": "user", "content": message}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        return completion.choices[0].message.content
        
    except Exception as e:
        print(f'Error generating text content: {e}')
        return f"テキスト内容生成エラー: {str(e)}"


# === 自分史用のテキスト生成機能 ===

def generate_memoir_text(text_type: str, data: Dict[str, Any]) -> str:
    """自分史用のテキストを生成
    
    Args:
        text_type: "profile" または "timeline_description"
        data: 生成に必要なデータ
    
    Returns:
        生成されたテキスト
    """
    try:
        if text_type == "profile":
            return generate_profile_text(data)
        elif text_type == "timeline_description":
            return generate_timeline_description(data)
        else:
            raise ValueError(f"Unknown text type: {text_type}")
    except Exception as e:
        print(f'Error generating memoir text: {e}')
        raise


def generate_profile_text(data: Dict[str, Any]) -> str:
    """プロフィール文章を生成
    
    Args:
        data: {
            "name": "名前",
            "birthDate": "生年月日",
            "birthPlace": "出身地",
            "occupation": "職業",
            "hobbies": ["趣味1", "趣味2"]
        }
    
    Returns:
        生成されたプロフィール文章
    """
    try:
        name = data.get("name", "")
        birth_date = data.get("birthDate", "")
        birth_place = data.get("birthPlace", "")
        occupation = data.get("occupation", "")
        hobbies = data.get("hobbies", [])
        
        # プロンプトを構築
        prompt = "以下の情報から、自分史のプロフィール文章を生成してください。\n"
        prompt += "親しみやすく、読みやすい文章でお願いします。\n"
        prompt += "自然な流れで、温かみのある文章にしてください。\n\n"
        
        if name:
            prompt += f"名前: {name}\n"
        if birth_date:
            prompt += f"生年月日: {birth_date}\n"
        if birth_place:
            prompt += f"出身地: {birth_place}\n"
        if occupation:
            prompt += f"職業: {occupation}\n"
        if hobbies:
            hobbies_str = "、".join(hobbies) if isinstance(hobbies, list) else hobbies
            prompt += f"趣味: {hobbies_str}\n"
        
        prompt += "\n150〜200文字程度で、自己紹介文を作成してください。"
        
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "あなたは自分史作成の専門家です。人生のストーリーを温かく、親しみやすい文章で表現するのが得意です。"
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.8
        )
        
        return completion.choices[0].message.content.strip()
        
    except Exception as e:
        print(f'Error generating profile text: {e}')
        raise Exception(f"プロフィール文章の生成に失敗しました: {str(e)}")


def generate_timeline_description(data: Dict[str, Any]) -> str:
    """年表の説明文を生成
    
    Args:
        data: {
            "year": 1985,
            "title": "小学校入学"
        }
    
    Returns:
        生成された説明文
    """
    try:
        year = data.get("year", "")
        title = data.get("title", "")
        
        if not year or not title:
            raise ValueError("年とタイトルは必須です")
        
        # プロンプトを構築
        prompt = f"自分史の年表で、以下の出来事についての説明文を生成してください。\n\n"
        prompt += f"年: {year}年\n"
        prompt += f"出来事: {title}\n\n"
        prompt += "当時の気持ちや状況を想像して、温かみのある文章で説明してください。\n"
        prompt += "100〜150文字程度でお願いします。"
        
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "あなたは自分史作成の専門家です。人生の重要な出来事を、感動的で心温まる文章で表現するのが得意です。"
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.8
        )
        
        return completion.choices[0].message.content.strip()
        
    except Exception as e:
        print(f'Error generating timeline description: {e}')
        raise Exception(f"説明文の生成に失敗しました: {str(e)}")


# グローバルインスタンス（互換性のため）
openai_service = openai_client

