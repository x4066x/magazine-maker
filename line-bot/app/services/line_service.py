from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    PushMessageRequest,
    TextMessage,
    ImageMessage,
    FlexMessage,
    FlexBubble,
    FlexBox,
    FlexText,
    FlexButton,
    URIAction
)
from linebot.v3.webhook import WebhookHandler
from linebot.v3.webhooks import (
    MessageEvent, 
    TextMessageContent,
    ImageMessageContent
)
from typing import Dict, Any
from pathlib import Path
from ..config import settings
from .file_service import file_service
from .memoir_service import memoir_service
from .quick_memoir_service import quick_memoir_service
from .photo_memoir_service import photo_memoir_service
from .openai_service import get_chatgpt_response

# LINE Bot API設定
configuration = Configuration(access_token=settings.CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.CHANNEL_SECRET)

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
    file_url = file_service.get_file_url(file_metadata['file_id'], settings.BASE_URL)
    
    if message_type == 'image':
        return ImageMessage(
            original_content_url=file_url,
            preview_image_url=file_url  # プレビュー画像も同じURLを使用
        )
    else:
        # その他のファイルタイプはテキストメッセージで代替
        return TextMessage(text=f"ファイル: {file_metadata.get('original_filename', 'file')}\n{file_url}")

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

def send_push_message(user_id: str, text: str) -> None:
    """プッシュメッセージを送信（reply_tokenが期限切れの場合に使用）"""
    try:
        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)
            
            push_message = TextMessage(text=text)
            
            response = messaging_api.push_message(
                PushMessageRequest(
                    to=user_id,
                    messages=[push_message]
                )
            )
            
            print(f'Push message sent successfully: {response}')
            
    except Exception as e:
        print(f'Error sending push message: {e}')

def send_text_message_with_fallback(reply_token: str, user_id: str, text: str) -> None:
    """テキストメッセージを送信（reply_tokenが失敗した場合はpush messageを使用）"""
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
        error_message = str(e)
        if "Invalid reply token" in error_message or "400" in error_message:
            print(f'Reply token expired, sending push message instead: {e}')
            send_push_message(user_id, text)
        else:
            print(f'Error sending text message: {e}')
            # 最後の手段としてpush messageを試行
            try:
                send_push_message(user_id, text)
            except Exception as push_error:
                print(f'Error sending push message as fallback: {push_error}')

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


def send_memoir_complete_message(reply_token: str, user_id: str, pdf_url: str, edit_url: str) -> None:
    """自分史完成メッセージ（Flex Message）を送信"""
    try:
        flex_message = FlexMessage(
            alt_text="✨ 自分史が完成しました！",
            contents=FlexBubble(
                size="kilo",
                header=FlexBox(
                    layout="vertical",
                    contents=[
                        FlexText(
                            text="✨ 自分史完成！",
                            weight="bold",
                            size="xl",
                            color="#FFFFFF"
                        )
                    ],
                    background_color="#6366F1",
                    padding_all="20px"
                ),
                body=FlexBox(
                    layout="vertical",
                    contents=[
                        FlexText(
                            text="プレビューPDFを生成しました",
                            size="md",
                            color="#333333",
                            margin="md"
                        ),
                        FlexText(
                            text="下のボタンから内容を編集できます",
                            size="sm",
                            color="#999999",
                            margin="md",
                            wrap=True
                        )
                    ],
                    spacing="md",
                    padding_all="20px"
                ),
                footer=FlexBox(
                    layout="vertical",
                    contents=[
                        FlexButton(
                            action=URIAction(
                                label="📄 PDFを見る",
                                uri=pdf_url
                            ),
                            style="primary",
                            color="#6366F1",
                            height="sm"
                        ),
                        FlexButton(
                            action=URIAction(
                                label="✏️ 内容を編集",
                                uri=edit_url
                            ),
                            style="primary",
                            color="#10B981",
                            height="sm",
                            margin="md"
                        )
                    ],
                    spacing="sm",
                    padding_all="20px"
                )
            )
        )
        
        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)
            
            response = messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[flex_message]
                )
            )
            
            print(f'Flex message sent successfully: {response}')
            
    except Exception as e:
        error_message = str(e)
        if "Invalid reply token" in error_message or "400" in error_message:
            print(f'Reply token expired, sending push message instead: {e}')
            # Flex MessageはPush Messageとしても送信可能
            try:
                with ApiClient(configuration) as api_client:
                    messaging_api = MessagingApi(api_client)
                    messaging_api.push_message(
                        PushMessageRequest(
                            to=user_id,
                            messages=[flex_message]
                        )
                    )
            except Exception as push_error:
                print(f'Error sending push message: {push_error}')
                # フォールバック: 通常のテキストメッセージ
                fallback_text = (
                    f"✨ 自分史が完成しました！\n\n"
                    f"📄 PDF: {pdf_url}\n"
                    f"✏️ 編集: {edit_url}"
                )
                send_push_message(user_id, fallback_text)
        else:
            print(f'Error sending flex message: {e}')
            # フォールバック: 通常のテキストメッセージ
            fallback_text = (
                f"✨ 自分史が完成しました！\n\n"
                f"📄 PDF: {pdf_url}\n"
                f"✏️ 編集: {edit_url}"
            )
            send_push_message(user_id, fallback_text)


def send_memoir_updated_message(user_id: str, pdf_url: str, edit_url: str) -> None:
    """自分史更新メッセージ（Flex Message）をプッシュ送信"""
    try:
        flex_message = FlexMessage(
            alt_text="✨ 自分史を更新しました！",
            contents=FlexBubble(
                size="kilo",
                header=FlexBox(
                    layout="vertical",
                    contents=[
                        FlexText(
                            text="✨ 更新完了！",
                            weight="bold",
                            size="xl",
                            color="#FFFFFF"
                        )
                    ],
                    background_color="#10B981",
                    padding_all="20px"
                ),
                body=FlexBox(
                    layout="vertical",
                    contents=[
                        FlexText(
                            text="自分史を更新しました",
                            size="md",
                            color="#333333",
                            margin="md"
                        ),
                        FlexText(
                            text="更新したPDFをご確認ください",
                            size="sm",
                            color="#999999",
                            margin="md",
                            wrap=True
                        )
                    ],
                    spacing="md",
                    padding_all="20px"
                ),
                footer=FlexBox(
                    layout="vertical",
                    contents=[
                        FlexButton(
                            action=URIAction(
                                label="📄 PDFを見る",
                                uri=pdf_url
                            ),
                            style="primary",
                            color="#10B981",
                            height="sm"
                        ),
                        FlexButton(
                            action=URIAction(
                                label="✏️ さらに編集",
                                uri=edit_url
                            ),
                            style="link",
                            height="sm",
                            margin="md"
                        )
                    ],
                    spacing="sm",
                    padding_all="20px"
                )
            )
        )
        
        # Push Messageとして送信（reply_tokenなし）
        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)
            messaging_api.push_message(
                PushMessageRequest(
                    to=user_id,
                    messages=[flex_message]
                )
            )
            print(f'Updated memoir flex message sent successfully to {user_id}')
            
    except Exception as e:
        print(f'Error sending updated memoir flex message: {e}')
        # フォールバック: 通常のテキストメッセージ
        fallback_text = (
            f"✨ 自分史を更新しました！\n\n"
            f"📄 PDF: {pdf_url}\n"
            f"✏️ さらに編集: {edit_url}"
        )
        send_push_message(user_id, fallback_text)


# テキストメッセージの処理
@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event: MessageEvent):
    """LINE テキストメッセージイベントを処理"""
    print(f'Received text message event: {event}')
    
    # メッセージ内容の確認
    print(f'Message ID: {event.message.id}')
    print(f'Message text: {event.message.text}')
    print(f'Reply token: {event.reply_token}')
    
    user_message = event.message.text
    user_id = event.source.user_id
    
    # 写真フロー: セッションを確認（最優先）
    photo_session = photo_memoir_service.get_session_by_user(user_id)
    
    # 写真フロー: 写真収集中に「完了」
    if photo_session and photo_session.state == "collecting_photos" and ("完了" in user_message or "おわり" in user_message or "終わり" in user_message):
        try:
            success, response = photo_memoir_service.finish_photo_collection(photo_session)
            send_text_message_with_fallback(event.reply_token, user_id, response)
            
            if success:
                # 最初の質問を送信
                question_info = photo_memoir_service.get_current_question(photo_session)
                if question_info:
                    question, photo, q_num = question_info
                    send_push_message(user_id, question)
            return
        except Exception as e:
            error_message = f"エラーが発生しました: {str(e)}"
            send_text_message_with_fallback(event.reply_token, user_id, error_message)
            return
    
    # 写真フロー: 質問に対する回答
    if photo_session and photo_session.state == "questioning":
        try:
            response_msg, needs_action = photo_memoir_service.process_answer(photo_session, user_message)
            send_text_message_with_fallback(event.reply_token, user_id, response_msg)
            
            if needs_action:
                # ストーリー生成が必要
                import threading
                
                def generate_story_async():
                    try:
                        photo = photo_session.get_current_photo()
                        if photo:
                            # ストーリー生成
                            story = photo_memoir_service.generate_story_for_photo(photo)
                            photo.generated_story = story
                            photo_session.state = "story_generated"
                            
                            # 承認メッセージを送信
                            approval_msg = photo_memoir_service.get_story_approval_message(photo_session, story)
                            send_push_message(user_id, approval_msg)
                    except Exception as e:
                        error_msg = f"ストーリー生成中にエラーが発生しました: {str(e)}"
                        send_push_message(user_id, error_msg)
                
                story_thread = threading.Thread(target=generate_story_async)
                story_thread.start()
            
            return
        except Exception as e:
            error_message = f"エラーが発生しました: {str(e)}"
            send_text_message_with_fallback(event.reply_token, user_id, error_message)
            return
    
    # 写真フロー: ストーリー承認・再生成
    if photo_session and photo_session.state == "story_generated":
        try:
            response_msg, move_next = photo_memoir_service.handle_story_approval(photo_session, user_message)
            send_text_message_with_fallback(event.reply_token, user_id, response_msg)
            
            if move_next:
                import threading
                
                def handle_next_action():
                    try:
                        if photo_session.state == "completed":
                            # 全写真完了 → PDF生成
                            pdf_result = photo_memoir_service.generate_pdf(photo_session)
                            
                            # PDFファイルを保存
                            file_metadata = file_service.save_file(
                                pdf_result["pdf_buffer"],
                                pdf_result["filename"],
                                "application/pdf"
                            )
                            
                            pdf_url = file_service.get_file_url(file_metadata['file_id'], settings.BASE_URL)
                            
                            success_message = (
                                f"✨ 写真自分史が完成しました！\n\n"
                                f"📄 PDF: {pdf_url}\n"
                                f"ファイル名: {pdf_result['filename']}\n"
                                f"サイズ: {pdf_result['size']:,} bytes"
                            )
                            send_push_message(user_id, success_message)
                        
                        elif "再生成" in response_msg:
                            # 再生成
                            photo = photo_session.get_current_photo()
                            if photo:
                                story = photo_memoir_service.generate_story_for_photo(photo)
                                photo.generated_story = story
                                
                                approval_msg = photo_memoir_service.get_story_approval_message(photo_session, story)
                                send_push_message(user_id, approval_msg)
                        
                        else:
                            # 次の写真の最初の質問を送信
                            question_info = photo_memoir_service.get_current_question(photo_session)
                            if question_info:
                                question, photo, q_num = question_info
                                send_push_message(user_id, question)
                    
                    except Exception as e:
                        error_msg = f"処理中にエラーが発生しました: {str(e)}"
                        send_push_message(user_id, error_msg)
                
                action_thread = threading.Thread(target=handle_next_action)
                action_thread.start()
            
            return
        except Exception as e:
            error_message = f"エラーが発生しました: {str(e)}"
            send_text_message_with_fallback(event.reply_token, user_id, error_message)
            return
    
    # 簡易フローのセッションを確認（優先）
    quick_session = quick_memoir_service.get_session_by_user(user_id)
    
    # 簡易フロー: 「作る」などのトリガーワード
    if quick_memoir_service.is_quick_create_request(user_message):
        try:
            session, response = quick_memoir_service.start_quick_create(user_id)
            send_text_message_with_fallback(event.reply_token, user_id, response)
            return
        except Exception as e:
            error_message = f"エラーが発生しました: {str(e)}"
            send_text_message_with_fallback(event.reply_token, user_id, error_message)
            return
    
    # 簡易フロー: タイトル待ち
    if quick_session and quick_session.state == "waiting_title":
        try:
            response = quick_memoir_service.process_title(quick_session, user_message)
            send_text_message_with_fallback(event.reply_token, user_id, response)
            return
        except Exception as e:
            error_message = f"エラーが発生しました: {str(e)}"
            send_text_message_with_fallback(event.reply_token, user_id, error_message)
            return
    
    # 特定のコマンドでファイル一覧表示
    if user_message.lower().startswith('ファイル一覧') or user_message.lower().startswith('files'):
        handle_file_list_command(event.reply_token)
    # サンプル確認コマンド
    elif user_message.lower() == 'サンプル確認':
        handle_sample_command(event.reply_token)
    else:
        # 通常のChatGPT応答
        handle_chatgpt_response(event)

def handle_sample_command(reply_token: str):
    """サンプルPDFファイル一覧を返信"""
    try:
        # samplesディレクトリのパス
        samples_dir = settings.SAMPLES_DIR
        
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
            file_url = f"{settings.BASE_URL}/samples/{pdf_file.name}"
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
            settings.BASE_URL,
            file_metadata['message_type']
        )
        
        user_id = event.source.user_id
        
        # 写真フロー: 写真収集中（最優先）
        photo_session = photo_memoir_service.get_session_by_user(user_id)
        if photo_session and photo_session.state == "collecting_photos":
            try:
                response_text = photo_memoir_service.add_photo(photo_session, file_url)
                send_text_message_with_fallback(event.reply_token, user_id, response_text)
                return
            except Exception as e:
                error_message = f"写真の処理中にエラーが発生しました: {str(e)}"
                send_text_message_with_fallback(event.reply_token, user_id, error_message)
                return
        
        # 簡易フロー: カバー写真待ち（優先）
        quick_session = quick_memoir_service.get_session_by_user(user_id)
        if quick_session and quick_session.state == "waiting_cover":
            try:
                # カバー写真を設定
                success, response_text = quick_memoir_service.process_cover_image(quick_session, file_url)
                send_text_message_with_fallback(event.reply_token, user_id, response_text)
                
                # 非同期でPDF生成
                if success:
                    import threading
                    
                    def generate_quick_pdf_async():
                        try:
                            # PDF生成（async関数をスレッド内で実行）
                            import asyncio
                            pdf_result = asyncio.run(quick_memoir_service.generate_quick_pdf(quick_session))
                            
                            # PDFファイルを保存
                            pdf_metadata = file_service.save_file(
                                pdf_result["pdf_buffer"],
                                pdf_result["filename"],
                                "application/pdf"
                            )
                            
                            # URLを生成
                            pdf_url = file_service.get_file_url(pdf_metadata['file_id'], settings.BASE_URL)
                            edit_url = f"{settings.BASE_URL}/liff/edit.html?session_id={quick_session.session_id}"
                            
                            # Flex Messageを送信（reply_tokenは期限切れなので、空文字でPush扱い）
                            send_memoir_complete_message("", user_id, pdf_url, edit_url)
                            
                        except Exception as e:
                            error_message = f"PDF生成中にエラーが発生しました: {str(e)}"
                            send_push_message(user_id, error_message)
                    
                    # 非同期スレッドを開始
                    pdf_thread = threading.Thread(target=generate_quick_pdf_async)
                    pdf_thread.start()
                
                return
            except Exception as e:
                error_message = f"画像の処理中にエラーが発生しました: {str(e)}"
                send_text_message_with_fallback(event.reply_token, user_id, error_message)
                return
        
        # セッション外での画像送信は無視
        response_text = "画像を受信しました。自分史を作成する場合は「作成」と送信してください。"
        send_text_message(event.reply_token, response_text)
        
    except Exception as e:
        print(f'Error handling image message: {e}')
        send_text_message(event.reply_token, "画像の処理中にエラーが発生しました。")

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
            file_url = file_service.get_file_url(file_info['file_id'], settings.BASE_URL, file_info['message_type'])
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

