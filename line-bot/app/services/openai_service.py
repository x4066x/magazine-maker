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

