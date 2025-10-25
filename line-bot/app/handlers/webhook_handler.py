from fastapi import Request, Response
from linebot.v3.exceptions import InvalidSignatureError
from ..services.line_service import handler

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

