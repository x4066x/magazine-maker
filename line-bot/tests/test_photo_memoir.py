"""
写真自分史サービスの簡易テスト
"""

import sys
from pathlib import Path

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.photo_memoir_service import photo_memoir_service, PhotoMemoirSession, PhotoItem


def test_basic_flow():
    """基本的なフローのテスト"""
    print("=" * 50)
    print("写真自分史サービス - 基本フローテスト")
    print("=" * 50)
    
    # 1. セッション開始
    print("\n1️⃣ セッション開始")
    session, response = photo_memoir_service.start_photo_memoir("test_user_123")
    print(f"✅ セッションID: {session.session_id}")
    print(f"✅ 状態: {session.state}")
    print(f"✅ レスポンス:\n{response}")
    
    # 2. 写真を追加
    print("\n2️⃣ 写真を追加")
    response1 = photo_memoir_service.add_photo(session, "https://example.com/photo1.jpg")
    print(f"✅ レスポンス1: {response1}")
    
    response2 = photo_memoir_service.add_photo(session, "https://example.com/photo2.jpg")
    print(f"✅ レスポンス2: {response2}")
    
    print(f"✅ 写真数: {len(session.photos)}")
    
    # 3. 写真収集完了
    print("\n3️⃣ 写真収集完了")
    success, response = photo_memoir_service.finish_photo_collection(session)
    print(f"✅ 成功: {success}")
    print(f"✅ 状態: {session.state}")
    print(f"✅ レスポンス:\n{response}")
    
    # 4. 質問を取得
    print("\n4️⃣ 質問を取得")
    question_info = photo_memoir_service.get_current_question(session)
    if question_info:
        question, photo, q_num = question_info
        print(f"✅ 質問{q_num}: {question}")
        print(f"✅ 写真ID: {photo.photo_id}")
    
    # 5. 回答を処理
    print("\n5️⃣ 回答を処理")
    response, needs_action = photo_memoir_service.process_answer(session, "2015年春です")
    print(f"✅ レスポンス: {response}")
    print(f"✅ アクション必要: {needs_action}")
    
    # 6. 次の質問を取得
    print("\n6️⃣ 次の質問を取得")
    question_info = photo_memoir_service.get_current_question(session)
    if question_info:
        question, photo, q_num = question_info
        print(f"✅ 質問{q_num}: {question}")
    
    # 7. 2つ目の回答
    print("\n7️⃣ 2つ目の回答を処理")
    response, needs_action = photo_memoir_service.process_answer(session, "代々木公園です")
    print(f"✅ レスポンス: {response}")
    print(f"✅ アクション必要: {needs_action}")
    
    # 8. 3つ目の回答（最後の質問）
    print("\n8️⃣ 3つ目の回答を処理（最後の質問）")
    response, needs_action = photo_memoir_service.process_answer(
        session, 
        "家族と一緒に花見をしました。子供が生まれて初めての春で、桜の下で家族写真を撮りました。"
    )
    print(f"✅ レスポンス: {response}")
    print(f"✅ アクション必要（ストーリー生成）: {needs_action}")
    
    # 9. 進捗確認
    print("\n9️⃣ 進捗確認")
    current, total = session.get_progress()
    print(f"✅ 進捗: {current}/{total}")
    
    # 10. データ構造確認
    print("\n🔟 データ構造確認")
    photo = session.get_current_photo()
    if photo:
        print(f"✅ 写真ID: {photo.photo_id}")
        print(f"✅ 写真URL: {photo.photo_url}")
        print(f"✅ 回答数: {len(photo.answers)}")
        print(f"✅ 回答内容:")
        for i, answer in enumerate(photo.answers, 1):
            print(f"   {i}. {answer}")
    
    print("\n" + "=" * 50)
    print("✨ 基本フローテスト完了！")
    print("=" * 50)
    
    return session


def test_story_approval():
    """ストーリー承認フローのテスト"""
    print("\n" + "=" * 50)
    print("ストーリー承認フローテスト")
    print("=" * 50)
    
    # セッションをセットアップ
    session, _ = photo_memoir_service.start_photo_memoir("test_user_456")
    photo_memoir_service.add_photo(session, "https://example.com/photo1.jpg")
    photo_memoir_service.finish_photo_collection(session)
    
    # 質問に回答
    for answer in ["2015年春", "代々木公園", "家族と花見をしました"]:
        photo_memoir_service.process_answer(session, answer)
    
    # ストーリーを生成（実際のAI生成をモック）
    photo = session.get_current_photo()
    photo.generated_story = "2015年春、代々木公園で家族と過ごした特別な花見の日。桜の下での家族写真は、今でも大切な思い出だ。"
    session.state = "story_generated"
    
    # 承認メッセージを取得
    print("\n1️⃣ 承認メッセージを取得")
    approval_msg = photo_memoir_service.get_story_approval_message(session, photo.generated_story)
    print(f"✅ メッセージ:\n{approval_msg}")
    
    # 承認
    print("\n2️⃣ 承認処理（👍）")
    response, move_next = photo_memoir_service.handle_story_approval(session, "👍")
    print(f"✅ レスポンス: {response}")
    print(f"✅ 次に進む: {move_next}")
    print(f"✅ 写真承認済み: {photo.story_approved}")
    
    print("\n" + "=" * 50)
    print("✨ ストーリー承認テスト完了！")
    print("=" * 50)


def test_template_data_preparation():
    """テンプレートデータ準備のテスト"""
    print("\n" + "=" * 50)
    print("テンプレートデータ準備テスト")
    print("=" * 50)
    
    # セッションをセットアップ
    session, _ = photo_memoir_service.start_photo_memoir("test_user_789")
    
    # 2枚の写真を追加
    photo_memoir_service.add_photo(session, "https://example.com/photo1.jpg")
    photo_memoir_service.add_photo(session, "https://example.com/photo2.jpg")
    
    # ストーリーを設定
    session.photos[0].generated_story = "1枚目のストーリー"
    session.photos[0].estimated_date = "2015年春"
    session.photos[0].estimated_location = "代々木公園"
    
    session.photos[1].generated_story = "2枚目のストーリー"
    session.photos[1].estimated_date = "2016年夏"
    session.photos[1].estimated_location = "海辺"
    
    # テンプレートデータを準備
    template_data = photo_memoir_service._prepare_template_data(session)
    
    print("\n✅ テンプレートデータ:")
    print(f"   タイトル: {template_data['title']}")
    print(f"   著者: {template_data['author']}")
    print(f"   日付: {template_data['date']}")
    print(f"   写真数: {template_data['photo_count']}")
    print(f"\n   ページ数: {len(template_data['pages'])}")
    
    for i, page in enumerate(template_data['pages'], 1):
        print(f"\n   📄 ページ{i}:")
        print(f"      画像: {page['image']}")
        print(f"      日付: {page['date']}")
        print(f"      場所: {page['location']}")
        print(f"      ストーリー: {page['story']}")
    
    print("\n" + "=" * 50)
    print("✨ テンプレートデータ準備テスト完了！")
    print("=" * 50)


if __name__ == "__main__":
    try:
        # 基本フローテスト
        test_basic_flow()
        
        # ストーリー承認テスト
        test_story_approval()
        
        # テンプレートデータ準備テスト
        test_template_data_preparation()
        
        print("\n" + "=" * 50)
        print("🎉 すべてのテスト完了！")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()

