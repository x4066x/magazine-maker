from fastapi import FastAPI, Request, Response
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.exceptions import InvalidSignatureError
import os
import json
import hashlib
import hmac
import base64
from dotenv import load_dotenv
from openai import AsyncOpenAI

# 環境変数を読み込む
load_dotenv()

app = FastAPI()

# LINE Botの設定
CHANNEL_ACCESS_TOKEN = os.environ.get('CHANNEL_ACCESS_TOKEN', 'your_channel_access_token')
CHANNEL_SECRET = os.environ.get('CHANNEL_SECRET', 'your_channel_secret')

# OpenAI APIの設定
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', 'your_openai_api_key')

# 環境変数の確認
print(f'CHANNEL_ACCESS_TOKEN: {CHANNEL_ACCESS_TOKEN[:5]}... (truncated for security)')
print(f'CHANNEL_SECRET: {CHANNEL_SECRET[:5]}... (truncated for security)')
print(f'OPENAI_API_KEY: {OPENAI_API_KEY[:5]}... (truncated for security)')

# LINE Bot API設定
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)

# OpenAI 非同期クライアント設定
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

def verify_signature(body: bytes, signature: str) -> bool:
    """LINE Webhook署名の検証"""
    if not signature:
        return False
    
    hash_value = hmac.new(
        CHANNEL_SECRET.encode('utf-8'),
        body,
        hashlib.sha256
    ).digest()
    expected_signature = base64.b64encode(hash_value).decode('utf-8')
    
    return hmac.compare_digest(signature, expected_signature)

async def get_chatgpt_response(user_message: str) -> str:
    """ユーザーのメッセージをChatGPTに送信し、短文レスポンスを取得"""
    try:
        completion = await openai_client.chat.completions.create(
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

async def handle_message_event(event_data: dict):
    """メッセージイベントを処理"""
    message = event_data.get('message', {})
    if message.get('type') != 'text':
        return  # テキストメッセージ以外は無視
    
    message_text = message.get('text', '')
    reply_token = event_data.get('replyToken', '')
    
    print(f'Message text: {message_text}')
    print(f'Reply token: {reply_token}')
    
    try:
        # ChatGPTからレスポンスを取得（非同期）
        chatgpt_response = await get_chatgpt_response(message_text)
        
        # LINE APIで返信送信（非同期）
        async with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)
            
            reply_message = TextMessage(text=chatgpt_response)
            
            await messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[reply_message]
                )
            )
            
            print(f'Reply sent successfully')
    except Exception as e:
        print(f'Error sending reply: {e}')
        import traceback
        traceback.print_exc()

@app.post('/callback')
async def webhook(request: Request):
    body = await request.body()
    signature = request.headers.get('X-Line-Signature', '')
    
    print('Received webhook request:')
    print(f'Body: {body.decode("utf-8")}')
    print(f'Signature: {signature}')
    
    # 署名検証
    if not verify_signature(body, signature):
        print('Invalid signature')
        return Response(status_code=400, content='Invalid signature')
    
    try:
        # JSONデータを解析
        webhook_data = json.loads(body.decode('utf-8'))
        events = webhook_data.get('events', [])
        
        # 各イベントを非同期で処理
        for event in events:
            if event.get('type') == 'message':
                await handle_message_event(event)
        
    except Exception as e:
        print(f'Error processing request: {e}')
        return Response(status_code=500, content=f'Error: {str(e)}')
    
    return Response(status_code=200, content='OK')

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)