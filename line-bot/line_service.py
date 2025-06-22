from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    TextMessage,
    ImageMessage,
    VideoMessage,
    AudioMessage
)
from linebot.v3.webhook import WebhookHandler
from linebot.v3.webhooks import (
    MessageEvent, 
    TextMessageContent,
    ImageMessageContent,
    VideoMessageContent,
    AudioMessageContent,
    FileMessageContent
)
import os
from dotenv import load_dotenv
from openai_service import get_chatgpt_response
from file_service import file_service
from typing import Dict, Any
from pathlib import Path

# 環境変数を読み込む
load_dotenv()

# LINE Botの設定
CHANNEL_ACCESS_TOKEN = os.environ.get('CHANNEL_ACCESS_TOKEN', 'your_channel_access_token')
CHANNEL_SECRET = os.environ.get('CHANNEL_SECRET', 'your_channel_secret')
BASE_URL = os.environ.get('BASE_URL', 'https://your-domain.com')  # 公開URL

# LINE Bot API設定
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

def download_file_from_line(message_id: str) -> bytes:
    """LINE Platform APIからファイルをダウンロード"""
    try:
        with ApiClient(configuration) as api_client:
            messaging_api_blob = MessagingApiBlob(api_client)
            
            # LINE Platform APIからファイルの内容を取得
            response = messaging_api_blob.get_message_content(message_id)
            
            if hasattr(response, 'data'):
                return response.data
            else:
                # レスポンスが直接バイナリデータの場合
                return response
                
    except Exception as e:
        print(f'Error downloading file from LINE: {e}')
        raise

def create_message_by_type(message_type: str, file_metadata: Dict[str, Any]) -> Any:
    """メッセージタイプに応じたメッセージオブジェクトを作成"""
    file_url = file_service.get_file_url(file_metadata['file_id'], BASE_URL)
    
    if message_type == 'image':
        return ImageMessage(
            original_content_url=file_url,
            preview_image_url=file_url  # プレビュー画像も同じURLを使用
        )
    elif message_type == 'video':
        return VideoMessage(
            original_content_url=file_url,
            preview_image_url=file_url  # サムネイル画像
        )
    elif message_type == 'audio':
        return AudioMessage(
            original_content_url=file_url,
            duration=5000  # デフォルト5秒（実際の長さが分かる場合は正確な値を設定）
        )
    elif message_type == 'file':
        # FileMessage は SDK v3 では利用できないため、テキストメッセージで代替
        return TextMessage(text=f"ファイルをダウンロード: {file_metadata.get('original_filename', 'file')}\n{file_url}")
    else:
        # デフォルトはテキストメッセージ
        return TextMessage(text=f"ファイルを受信しました: {file_metadata.get('original_filename', 'unknown')}")

def send_file_message(reply_token: str, file_metadata: Dict[str, Any]) -> None:
    """ファイルメッセージを送信"""
    try:
        message_type = file_metadata['message_type']
        message = create_message_by_type(message_type, file_metadata)
        
        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)
            
            response = messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[message]
                )
            )
            
            print(f'File message sent successfully: {response}')
            
    except Exception as e:
        print(f'Error sending file message: {e}')
        # ファイル送信に失敗した場合はテキストメッセージで通知
        send_text_message(reply_token, f"ファイルの送信に失敗しました: {str(e)}")

def send_text_message(reply_token: str, text: str) -> None:
    """テキストメッセージを送信"""
    try:
        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)
            
            reply_message = TextMessage(text=text)
            
            response = messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[reply_message]
                )
            )
            
            print(f'Text message sent successfully: {response}')
            
    except Exception as e:
        print(f'Error sending text message: {e}')

def send_multiple_messages(reply_token: str, messages: list) -> None:
    """複数のメッセージを送信"""
    try:
        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)
            
            response = messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=messages[:5]  # 最大5つまで
                )
            )
            
            print(f'Multiple messages sent successfully: {response}')
            
    except Exception as e:
        print(f'Error sending multiple messages: {e}')

# テキストメッセージの処理
@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event: MessageEvent):
    """LINE テキストメッセージイベントを処理"""
    print(f'Received text message event: {event}')
    
    # メッセージ内容の確認
    print(f'Message ID: {event.message.id}')
    print(f'Message text: {event.message.text}')
    print(f'Reply token: {event.reply_token}')
    
    user_message = event.message.text.lower()
    
    # 特定のコマンドでファイル一覧表示
    if user_message.startswith('ファイル一覧') or user_message.startswith('files'):
        handle_file_list_command(event.reply_token)
    # サンプル確認コマンド
    elif user_message == 'サンプル確認':
        handle_sample_command(event.reply_token)
    else:
        # 通常のChatGPT応答
        handle_chatgpt_response(event)

def handle_sample_command(reply_token: str):
    """サンプルPDFファイル一覧を返信"""
    try:
        # samplesディレクトリのパス
        samples_dir = Path("samples")
        
        if not samples_dir.exists():
            send_text_message(reply_token, "サンプルファイルディレクトリが見つかりません。")
            return
        
        # PDFファイルを検索
        pdf_files = list(samples_dir.glob("*.pdf"))
        
        if not pdf_files:
            send_text_message(reply_token, "サンプルPDFファイルが見つかりません。")
            return
        
        # ファイル一覧を作成
        response_text = "サンプルPDFファイル一覧：\n\n"
        for pdf_file in pdf_files:
            file_size = pdf_file.stat().st_size
            file_url = f"{BASE_URL}/samples/{pdf_file.name}"
            response_text += (
                f"📄 {pdf_file.name}\n"
                f"📦 サイズ: {file_size:,} bytes\n"
                f"🔗 URL: {file_url}\n\n"
            )
        
        send_text_message(reply_token, response_text)
        
    except Exception as e:
        print(f'Error handling sample command: {e}')
        send_text_message(reply_token, "サンプルファイルの処理中にエラーが発生しました。")

# 画像メッセージの処理
@handler.add(MessageEvent, message=ImageMessageContent)
def handle_image_message(event: MessageEvent):
    """LINE 画像メッセージイベントを処理"""
    print(f'Received image message event: {event}')
    
    try:
        # LINE Platform APIから画像をダウンロード
        image_data = download_file_from_line(event.message.id)
        
        # 画像ファイルを保存
        file_metadata = file_service.save_file(
            image_data,
            f"received_image_{event.message.id}.jpg",
            "image/jpeg"
        )
        
        # 画像のURLを生成
        file_url = file_service.get_file_url(
            file_metadata['file_id'],
            BASE_URL,
            file_metadata['message_type']
        )
        
        # レスポンスメッセージを送信
        response_text = (
            f"画像を受信しました！\n"
            f"ファイルサイズ: {file_metadata['file_size']} bytes\n"
            f"画像URL: {file_url}"
        )
        send_text_message(event.reply_token, response_text)
        
    except Exception as e:
        print(f'Error handling image message: {e}')
        send_text_message(event.reply_token, "画像の処理中にエラーが発生しました。")

# 動画メッセージの処理
@handler.add(MessageEvent, message=VideoMessageContent)
def handle_video_message(event: MessageEvent):
    """LINE 動画メッセージイベントを処理"""
    print(f'Received video message event: {event}')
    
    try:
        # LINE Platform APIから動画をダウンロード
        video_data = download_file_from_line(event.message.id)
        
        # 動画ファイルを保存
        file_metadata = file_service.save_file(
            video_data,
            f"received_video_{event.message.id}.mp4",
            "video/mp4"
        )
        
        # 動画のURLを生成
        file_url = file_service.get_file_url(
            file_metadata['file_id'],
            BASE_URL,
            file_metadata['message_type']
        )
        
        # レスポンスメッセージを送信
        response_text = (
            f"動画を受信しました！\n"
            f"ファイルサイズ: {file_metadata['file_size']} bytes\n"
            f"動画URL: {file_url}"
        )
        send_text_message(event.reply_token, response_text)
        
    except Exception as e:
        print(f'Error handling video message: {e}')
        send_text_message(event.reply_token, "動画の処理中にエラーが発生しました。")

# 音声メッセージの処理
@handler.add(MessageEvent, message=AudioMessageContent)
def handle_audio_message(event: MessageEvent):
    """LINE 音声メッセージイベントを処理"""
    print(f'Received audio message event: {event}')
    
    try:
        # LINE Platform APIから音声をダウンロード
        audio_data = download_file_from_line(event.message.id)
        
        # 音声ファイルを保存
        file_metadata = file_service.save_file(
            audio_data,
            f"received_audio_{event.message.id}.m4a",
            "audio/aac"
        )
        
        # 音声のURLを生成
        file_url = file_service.get_file_url(
            file_metadata['file_id'],
            BASE_URL,
            file_metadata['message_type']
        )
        
        # レスポンスメッセージを送信
        response_text = (
            f"音声を受信しました！\n"
            f"ファイルサイズ: {file_metadata['file_size']} bytes\n"
            f"音声URL: {file_url}"
        )
        send_text_message(event.reply_token, response_text)
        
    except Exception as e:
        print(f'Error handling audio message: {e}')
        send_text_message(event.reply_token, "音声の処理中にエラーが発生しました。")

# ファイルメッセージの処理
@handler.add(MessageEvent, message=FileMessageContent)
def handle_file_message(event: MessageEvent):
    """LINE ファイルメッセージイベントを処理"""
    print(f'Received file message event: {event}')
    
    try:
        # LINE Platform APIからファイルをダウンロード
        file_data = download_file_from_line(event.message.id)
        
        # ファイル名を取得（存在する場合）
        filename = getattr(event.message, 'file_name', f"received_file_{event.message.id}")
        
        # ファイルを保存
        file_metadata = file_service.save_file(
            file_data,
            filename,
            None  # Content-Typeはファイル名から推測
        )
        
        # レスポンスメッセージを送信
        response_text = f"ファイルを受信しました！\nファイル名: {filename}\nファイルサイズ: {file_metadata['file_size']} bytes"
        send_text_message(event.reply_token, response_text)
        
    except Exception as e:
        print(f'Error handling file message: {e}')
        send_text_message(event.reply_token, "ファイルの処理中にエラーが発生しました。")

def handle_file_list_command(reply_token: str):
    """ファイル一覧表示コマンドを処理"""
    try:
        files = file_service.list_files()
        
        if not files:
            send_text_message(reply_token, "保存されているファイルはありません。")
            return
        
        # ファイル一覧をテキストで表示
        file_list_text = "保存されているファイル:\n\n"
        for file_info in files[:10]:  # 最大10件まで表示
            file_url = file_service.get_file_url(file_info['file_id'], BASE_URL, file_info['message_type'])
            file_list_text += (
                f"{file_info['filename']} ({file_info['message_type']})\n"
                f"URL: {file_url}\n\n"
            )
        
        if len(files) > 10:
            file_list_text += f"... 他 {len(files) - 10} 件"
        
        send_text_message(reply_token, file_list_text)
        
    except Exception as e:
        print(f'Error handling file list command: {e}')
        send_text_message(reply_token, "ファイル一覧の取得に失敗しました。")

def handle_chatgpt_response(event: MessageEvent):
    """ChatGPT応答を処理"""
    try:
        # ChatGPTからレスポンスを取得
        chatgpt_response = get_chatgpt_response(event.message.text)
        send_text_message(event.reply_token, chatgpt_response)
        
    except Exception as e:
        print(f'Error handling ChatGPT response: {e}')
        send_text_message(event.reply_token, f"エラーが発生しました: {str(e)}")