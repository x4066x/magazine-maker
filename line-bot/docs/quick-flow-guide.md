# 簡易自分史作成フロー - 実装ガイド

## 🎉 実装完了！

簡単な入力でPDFを生成し、後から編集できる新しいフローを実装しました。

## 📝 実装内容

### 1. 新しいフロー

```
ユーザー: 「作る」
   ↓
Bot: 「タイトルを教えてください」
   ↓
ユーザー: 「私の人生物語」
   ↓
Bot: 「カバー写真を送ってください」
   ↓
ユーザー: [写真アップロード]
   ↓
Bot: 「PDFを生成中...⏳」
   ↓ (3〜5秒)
Bot: [Flex Messageカード]
     ✨ 自分史完成！
     📄 PDFを見る [ボタン]
     ✏️ 内容を編集 [ボタン]
   ↓
ユーザーが「✏️ 内容を編集」をタップ
   ↓
編集画面が開く（Webページ）
   - タイトル、サブタイトル、著者名
   - プロフィール（自己紹介、生年月日、出身地、職業、趣味）
     - 🤖 AIに文章を書いてもらう [ボタン]
   - 年表（出来事の追加・削除・並び替え）
     - 🤖 AIに文章を書いてもらう [ボタン]
   ↓
「💾 保存してPDF生成」ボタンをタップ
   ↓
Bot: 「✨ 自分史を更新しました！」
     [新しいPDF + 編集リンク]
```

### 2. 技術的な特徴

#### パフォーマンス最適化
- **高速な画像処理**: ローカルファイル直接コピーで3秒以内にPDF生成
- **非同期処理**: イベントループを適切に管理し、ブロッキングなし
- **セッション管理**: Single Source of Truth原則でデータの整合性を保証

#### UX改善
- **美しいFlex Message**: 落ち着いた色（インディゴ、エメラルドグリーン）
- **リアルタイムフィードバック**: 保存・更新時に視覚的なメッセージ
- **直感的な編集画面**: AI支援付きのフォーム

### 3. ファイル構成

#### 新規作成したファイル

1. **`app/services/quick_memoir_service.py`**
   - 簡易フロー用のサービス
   - タイトル + カバー写真でPDF生成
   - **async対応**: イベントループの問題を解決
   - セッション管理

2. **`liff/edit.html`**
   - 編集画面（HTML + CSS + JavaScript すべて1ファイル）
   - レスポンシブデザイン対応
   - AI文章生成機能付き

3. **`docs/quick-flow-guide.md`**（このファイル）
   - 実装ガイド

#### 更新したファイル

1. **`app/services/openai_service.py`**
   - `generate_memoir_text()`: 自分史用の文章生成
   - `generate_profile_text()`: プロフィール文章生成
   - `generate_timeline_description()`: 年表説明文生成

2. **`app/services/line_service.py`**
   - `send_memoir_complete_message()`: Flex Message送信
   - 簡易フローのハンドラー統合
   - 画像メッセージでカバー写真処理

3. **`app/api/routes.py`**
   - `GET /api/memoir/edit/{session_id}`: 編集データ取得
   - `POST /api/memoir/save/{session_id}`: データ保存＆PDF再生成
   - `POST /api/memoir/generate-text`: LLM文章生成

4. **`app/main.py`**
   - `/liff/` の静的ファイル配信を追加

5. **`docs/design.md`**
   - 新しい設計ドキュメントに完全刷新

## 🚀 使い方

### 1. サーバーを起動

```bash
cd line-bot
uv run python -m app.main
```

### 2. ngrokでトンネルを作成（開発時）

```bash
ngrok http 8000
```

### 3. LINE Developers コンソールで Webhook URL を設定

```
https://your-ngrok-url.ngrok.io/callback
```

### 4. 環境変数を設定

`.env` ファイルまたは環境変数に以下を設定：

```bash
# LINE Bot
CHANNEL_ACCESS_TOKEN=your_channel_access_token
CHANNEL_SECRET=your_channel_secret

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Auto-Designer (PDF生成サービス)
AUTO_DESIGNER_URL=http://localhost:3000

# BASE_URL（ngrokのURL）
BASE_URL=https://your-ngrok-url.ngrok.io
```

### 5. LINE Botで「作る」と送信

簡易フローが開始されます！

## 🎨 編集画面の機能

### 基本情報
- タイトル
- サブタイトル
- 著者名

### プロフィール
- 自己紹介文（AI生成可能）
- 生年月日
- 出身地
- 職業
- 趣味

### 年表
- 出来事の追加
- 年・タイトル・説明文
- 説明文のAI生成
- 削除

### AI文章生成
- プロフィール文章: 150〜200文字の自己紹介
- 年表説明文: 100〜150文字の出来事説明

## 📡 API エンドポイント

### 1. 編集データ取得

```bash
GET /api/memoir/edit/{session_id}

Response:
{
  "session_id": "quick_abc123",
  "user_id": "U1234567890",
  "data": {
    "title": "私の人生物語",
    "subtitle": "〜これまでの道のり〜",
    "author": "あなた",
    "cover_image_url": "https://...",
    "profile": {...},
    "timeline": [...]
  }
}
```

### 2. データ保存＆PDF再生成

```bash
POST /api/memoir/save/{session_id}
Content-Type: application/json

{
  "data": {
    "title": "私の人生物語",
    "author": "鈴木太郎",
    ...
  }
}

Response:
{
  "success": true,
  "pdf_url": "https://.../memoir_xxx.pdf",
  "message": "PDFを更新しました"
}
```

### 3. AI文章生成

```bash
POST /api/memoir/generate-text
Content-Type: application/json

{
  "type": "profile",
  "data": {
    "name": "鈴木太郎",
    "birthDate": "1985年3月15日",
    "birthPlace": "東京都",
    "occupation": "会社員",
    "hobbies": ["読書", "旅行"]
  }
}

Response:
{
  "success": true,
  "generated_text": "鈴木太郎は1985年3月15日、東京で生まれました。..."
}
```

## 🔧 カスタマイズ

### トリガーワードを変更

`app/services/quick_memoir_service.py` の `is_quick_create_request()`:

```python
trigger_keywords = ['作る', '作成', 'つくる', 'create', '自分史']
```

### AI生成のプロンプトを変更

`app/services/openai_service.py` の以下の関数：
- `generate_profile_text()`
- `generate_timeline_description()`

### 編集画面のデザインを変更

`liff/edit.html` の `<style>` セクション

## 🎯 次のステップ

### Phase 2: 機能拡張

- [ ] 画像アップロード機能（編集画面から）
- [ ] ドラッグ&ドロップで年表の並び替え
- [ ] テンプレート選択機能
- [ ] リアルタイムプレビュー

### Phase 3: LIFF化（オプション）

- [ ] LINE LIFF IDを取得・設定
- [ ] `liff.init()` と `liff.getProfile()` を追加
- [ ] LINEアプリ内で完結する体験

### Phase 4: UX改善

- [ ] 音声入力対応
- [ ] 画像の自動最適化
- [ ] PDFダウンロード機能
- [ ] SNSシェア機能

## 🐛 トラブルシューティング

### PDF生成に失敗する

1. `AUTO_DESIGNER_URL` が正しく設定されているか確認
2. Auto-Designerサービスが起動しているか確認
3. ログを確認: `print(f'PDF generation error: {e}')`

### 編集画面が表示されない

1. `BASE_URL` が正しく設定されているか確認
2. `/liff/edit.html` にアクセスできるか確認
3. ブラウザのコンソールでエラーを確認

### AI文章生成に失敗する

1. `OPENAI_API_KEY` が正しく設定されているか確認
2. OpenAI APIの残高を確認
3. レート制限に達していないか確認

### Flex Messageが送信されない

1. LINE Botの権限を確認
2. `send_memoir_complete_message()` のログを確認
3. フォールバックのテキストメッセージが送信されているか確認

## 📚 参考資料

- [LINE Messaging API](https://developers.line.biz/ja/docs/messaging-api/)
- [LINE Flex Message](https://developers.line.biz/ja/docs/messaging-api/using-flex-messages/)
- [OpenAI API](https://platform.openai.com/docs/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Vivliostyle](https://vivliostyle.org/)

## 🎊 完成！

これで、ユーザーは「作る」と入力するだけで、すぐに自分史のPDFを手に入れることができます。
後から編集画面で詳細を追加・修正でき、AI が文章生成をサポートしてくれます。

楽しい自分史作成体験をお楽しみください！✨

---

## 🚨 現在のフローの課題と新アプローチ

### 現在のフローの問題点

#### 1. **編集フォームの限界**
現在の `edit.html` は固定されたフォームフィールドを持っています：
- プロフィール（生年月日、出身地、職業、趣味）
- 年表（年、タイトル、説明文）

**問題**:
- テンプレートにない項目は入力しても反映されない
- ユーザーごとの個別ストーリーに対応できない
- フォームを埋める作業が心理的ハードルになる

#### 2. **写真の活用不足**
- カバー写真1枚のみ
- 他の写真を追加する導線がない
- 視覚的な魅力が不足

#### 3. **AI活用の矛盾**
- 「AIが書いてくれる」のに、先に情報入力が必要
- 生成された文章の修正・再生成がしづらい

### 💡 新アプローチ: 写真中心・対話ベース自分史

## 🎯 新フロー概要

**コンセプト**: 「写真を見ながら、AIと対話するだけで自分史が完成」

```
👤 ユーザー: 「自分史作る」

🤖 Bot: 「写真を送ってください（複数枚OK）📸
     送り終わったら「完了」と送信してください」

👤 ユーザー: [写真1] [写真2] [写真3] ... [写真N]
👤 ユーザー: 「完了」

🤖 Bot: 「写真を5枚受け取りました！
     これから写真について質問するので、答えてください
     テキストでも音声でも大丈夫です🎤」
     
     [写真1を表示]
     「この写真について教えてください」
     
     ・いつ頃の写真ですか？
     ・どこで撮った写真ですか？
     ・この時の思い出を教えてください

👤 ユーザー: 「2015年春、桜の下で家族と撮りました。
          子供が生まれて初めてのお花見で...」

🤖 Bot: 「素敵な思い出ですね✨
     AIが文章をまとめています...」
     
     【生成されたストーリー】
     『2015年春、満開の桜の下で家族と過ごした特別な日。
     子供が生まれて初めてのお花見は、新しい命の誕生を
     祝福するような穏やかな時間だった。』
     
     「このままでOKですか？」
     👍 いいね / ✏️ 修正 / 🔄 再生成

👤 ユーザー: 👍

🤖 Bot: [写真2を表示]
     「2枚目の写真です（5枚中2枚目）」
     「この写真について教えてください」
     ...

[全写真の対話完了]

🤖 Bot: 「すべての写真のストーリーが完成しました！
     PDFを生成しています...⏳」
     
🤖 Bot: ✨ 完成しました！
     📄 PDFを見る
     📸 写真を追加
```

## 📦 実装内容 (Phase 1)

### 新規ファイル

1. **`app/services/photo_memoir_service.py`**
   - 写真収集フロー管理
   - 質問・回答処理
   - ストーリー生成
   - PDF生成

### データ構造

```python
@dataclass
class PhotoMemoirSession:
    session_id: str
    user_id: str
    state: str  # "collecting_photos" | "questioning" | "generating" | "completed"
    photos: List[PhotoItem] = field(default_factory=list)
    current_photo_index: int = 0
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class PhotoItem:
    photo_id: str
    photo_url: str
    uploaded_at: datetime
    # 回答
    answers: List[str] = field(default_factory=list)
    # 生成されたストーリー
    generated_story: Optional[str] = None
    story_approved: bool = False
```

## 🎨 特徴

### ✅ ユーザーにとってのメリット
1. **簡単**: フォーム入力不要、会話だけで完結
2. **楽しい**: 写真を見ながら思い出を語る体験
3. **柔軟**: 写真の枚数制限なし、自由に表現
4. **美しい**: AIが文章を整えるので、誰でもきれいな自分史

### ✅ 技術的なメリット
1. **テンプレート依存なし**: 写真とストーリーの単純な組み合わせ
2. **AI活用の最大化**: 質問→回答→生成の自然な流れ
3. **拡張性**: 音声入力、写真分析など追加しやすい

## 🚀 実装フェーズ

### Phase 1: MVP（最小実装）🎯 次に実装
- [ ] PhotoMemoirService 作成
- [ ] 写真収集フロー（複数枚対応）
- [ ] 固定質問での対話
- [ ] テキスト回答の処理
- [ ] ストーリー生成（OpenAI）
- [ ] 1写真1ページのPDF生成
- [ ] 承認・再生成フロー

### Phase 2: 拡張機能
- [ ] 音声入力対応（Whisper API）
- [ ] 写真分析（Vision API）
- [ ] 動的質問生成
- [ ] 時系列自動推測
- [ ] スキップ機能

### Phase 3: UX改善
- [ ] プログレスバー表示
- [ ] 途中保存・再開機能
- [ ] 写真の追加・削除
- [ ] カバー自動生成

## 📝 使い方（実装後）

### 1. 写真を複数枚送信

```
ユーザー: 「自分史作る」
Bot: 「写真を送ってください」
ユーザー: [写真1] [写真2] [写真3]
ユーザー: 「完了」
```

### 2. 対話形式で回答

```
Bot: [写真1表示]
     「いつ頃の写真ですか？」
ユーザー: 「2015年春です」

Bot: 「どこで撮った写真ですか？」
ユーザー: 「代々木公園で家族と花見をしました」

Bot: 「この時の思い出を教えてください」
ユーザー: 「子供が生まれて初めての花見で、
      桜の下で家族写真を撮りました」
```

### 3. AI生成の確認

```
Bot: 「こんな感じでまとめました：
     『2015年春、代々木公園で家族と過ごした
     特別な花見の日。子供が生まれて初めての
     桜の下での家族写真は、今でも大切な思い出だ。』」
     
     👍 いいね / 🔄 再生成 / ✏️ 修正

ユーザー: 👍
```

### 4. 繰り返し→完成

```
Bot: [写真2表示]
     「2枚目の写真です（5枚中2枚目）」
     ...

[全写真完了]

Bot: 「✨ 完成しました！」
     📄 PDFを見る
```

## 🎯 実装開始

次のセクションから、Phase 1 の実装を開始します。

---

## 📚 参考情報

- **詳細設計**: `docs/design.md` の「写真中心・対話ベース自分史」セクション
- **OpenAI Whisper API**: 音声→テキスト変換
- **OpenAI Vision API**: 写真内容分析（Phase 2）

