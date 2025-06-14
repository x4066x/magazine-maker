from fastapi import FastAPI, Request, Response
from linebot.v3.messaging import MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhook import WebhookHandler, WebhookPayload
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

app = FastAPI()

# LINE Botの設定
CHANNEL_ACCESS_TOKEN = os.environ.get('CHANNEL_ACCESS_TOKEN', 'your_channel_access_token')
CHANNEL_SECRET = os.environ.get('CHANNEL_SECRET', 'your_channel_secret')

# 環境変数の確認
print(f'CHANNEL_ACCESS_TOKEN: {CHANNEL_ACCESS_TOKEN[:5]}... (truncated for security)')
print(f'CHANNEL_SECRET: {CHANNEL_SECRET[:5]}... (truncated for security)')

handler = WebhookHandler(CHANNEL_SECRET)

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
    except InvalidSignatureError:
        print('Invalid signature')
        return Response(status_code=400, content='Invalid signature')
    except Exception as e:
        print(f'Error processing request: {e}')
        return Response(status_code=500, content=f'Error: {str(e)}')
    
    return Response(status_code=200, content='OK')

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    messaging_api = MessagingApi(CHANNEL_ACCESS_TOKEN)
    messaging_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=event.message.text).as_json_dict()]
        )
    )

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)