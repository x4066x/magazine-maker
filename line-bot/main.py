from fastapi import FastAPI, Request, Response
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhook import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import os
from dotenv import load_dotenv
from openai import OpenAI

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
handler = WebhookHandler(CHANNEL_SECRET)

# OpenAI クライアント設定
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def get_chatgpt_response(user_message: str) -> str:
    """ユーザーのメッセージをChatGPTに送信し、短文レスポンスを取得"""
    try:
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

@app.post('/callback')
async def webhook(request: Request):
    body = await request.body()
    signature = request.headers.get('X-Line-Signature', '')
    
    # コンソールにリクエストデータを表示
    print('Received webhook request:')
    print(f'Body: {body.decode("utf-8")}')
    print(f'Signature: {signature}')
    
    # Webhookハンドラーを使用して処理
    try:
        body_str = body.decode('utf-8')
        handler.handle(body_str, signature)
    except InvalidSignatureError as e:
        print(f'Invalid signature error: {e}')
        return Response(status_code=400, content='Invalid signature')
    except Exception as e:
        print(f'Error processing request: {e}')
        return Response(status_code=500, content=f'Error: {str(e)}')
    
    return Response(status_code=200, content='OK')

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent):
    print(f'Received message event: {event}')
    
    # メッセージ内容の確認
    print(f'Message ID: {event.message.id}')
    print(f'Message text: {event.message.text}')
    print(f'Reply token: {event.reply_token}')
    
    try:
        # ChatGPTからレスポンスを取得
        chatgpt_response = get_chatgpt_response(event.message.text)
        
        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)
            
            # 返信メッセージの作成
            reply_message = TextMessage(text=chatgpt_response)
            
            # 返信送信
            response = messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[reply_message]
                )
            )
            
            print(f'Reply sent successfully: {response}')
    except Exception as e:
        print(f'Error sending reply: {e}')
        print(f'Error type: {type(e)}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)