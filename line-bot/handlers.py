from fastapi import Request, Response
from linebot.v3.exceptions import InvalidSignatureError
from line_service import handler
import os
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

# LINE Botの設定
CHANNEL_ACCESS_TOKEN = os.environ.get('CHANNEL_ACCESS_TOKEN', 'your_channel_access_token')
CHANNEL_SECRET = os.environ.get('CHANNEL_SECRET', 'your_channel_secret')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', 'your_openai_api_key')

# 環境変数の確認
print(f'CHANNEL_ACCESS_TOKEN: {CHANNEL_ACCESS_TOKEN[:5]}... (truncated for security)')
print(f'CHANNEL_SECRET: {CHANNEL_SECRET[:5]}... (truncated for security)')
print(f'OPENAI_API_KEY: {OPENAI_API_KEY[:5]}... (truncated for security)')

async def handle_webhook(request: Request):
    """LINE Webhook を処理"""
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