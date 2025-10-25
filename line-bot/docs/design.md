# LINE Bot 自分史作成サービス - 全体設計（参考用）

⚠️ **注意**: このドキュメントには古い情報や未実装の機能が含まれています。

**最新の実装内容**については、以下のドキュメントを参照してください：
- **拡張版簡易フロー**: [extended-quick-flow-guide.md](./extended-quick-flow-guide.md)
- **メディアテンプレート**: [media-template-guide.md](./media-template-guide.md)

---

## 参考: 初期の設計思想

このセクションは、初期設計の記録として残しています。

## 🎯 目的

ユーザーの入力負担を最小限にし、すぐにプレビューできる体験を提供することで、入力意欲を引き出し、高いコンバージョン率を実現する。

## 📋 課題と解決策

### 現状の課題
- 6ターンのチャットフローで詳細な情報を収集する必要がある
- ユーザーの入力負担が大きく、途中離脱が発生しやすい
- 成果物を見るまでに時間がかかり、モチベーションが維持しにくい

### 解決策
- **最小限の入力でPDF生成**：タイトル + カバー写真のみで即座にPDF生成
- **即座のプレビュー提供**：簡単な情報で一旦PDFを生成し、すぐに見せる
- **LIFF編集画面**：詳細な編集はHTML編集画面で直感的に操作
- **LLM支援**：文章生成はAIがサポート
- **高速な画像処理**：ローカルファイル直接コピーで30秒 → 3秒に短縮

## 🔄 チャットフロー

### 統一された入口

**重要**: 2025-10-25更新 - すべてのフローの入口を「作成」キーワードに統一しました。

```
ユーザー
  ↓ 「作る」「作成」「つくる」などのトリガーワード（統一入口）
Bot: タイトルを教えてください
  ↓
ユーザー: 「私の人生物語」
  ↓
Bot: カバー写真を送ってください
  ↓
ユーザー: [写真アップロード]
  ↓
Bot: PDFを生成中...
  ↓ (3〜5秒)
Bot: ✨完成しました！
     📄 プレビューPDF: [URL]
     ✏️ 内容を編集: [LIFF編集画面URL]
  ↓
ユーザーがLIFF編集画面で編集
  - テキスト追加・編集（LLMによる文章生成支援）
  - 画像の追加・削除・並び替え
  - レイアウト選択（テンプレート切り替え）
  ↓
「保存」ボタンクリック
  ↓
新しいPDFを生成して返す
  ↓
Bot: 🎉 更新されました！
     📄 最新PDF: [URL]
     ✏️ さらに編集: [LIFF編集画面URL]
```

### 削除された入口（2025-10-25）

以下の入口は削除され、すべて「作成」キーワードに統一されました：

- ❌ 「写真で作る」「写真自分史」「フォト」（写真自分史の直接トリガー）
- ❌ 「自分史作成」「memoir」「人生の歩み」（従来自分史の直接トリガー）
- ❌ セッション外での画像・動画・音声・ファイル送信による直接開始

**理由**: ユーザー体験を統一し、混乱を避けるため

## 🎨 初期PDF生成の仕様

### 最小限の入力項目
1. **タイトル**（必須）
2. **カバー写真**（必須）

### 自動生成される内容
- **著者名**: "あなた" または ユーザーの表示名
- **プロフィール**: LLMが生成（後で編集可能）
- **年表**: 空の状態でテンプレート表示（後で編集可能）
- **日付**: 現在の年月日

### 使用するテンプレート
- **タイトルページ**: `vivliostyle/sample/templates/modern/title/modern-vertical-cover/`
- **コンテンツページ**: `vivliostyle/sample/templates/modern/single/vertical-central-image-single/`

## 🖥️ LIFF編集画面の仕様

### 編集機能
1. **基本情報編集**
   - タイトル
   - サブタイトル
   - 著者名
   - カバー写真（変更・削除）

2. **プロフィール編集**
   - 自己紹介文（テキストエリア）
   - 「AIに文章を書いてもらう」ボタン → LLMが生成
   - 生年月日
   - 出身地
   - 職業
   - 趣味

3. **年表編集**
   - 年表項目の追加・削除・並び替え（ドラッグ&ドロップ）
   - 各項目：
     - 年
     - タイトル
     - 説明文
     - 画像（アップロード可能）
   - 「AIに文章を書いてもらう」ボタン → タイトルから説明文を生成

4. **レイアウト選択**
   - テンプレート一覧から選択
     - modern-vertical-cover
     - modern-horizontal-cover
     - vertical-central-image-single
     - vertical-landscape-image-single
     - 他

5. **プレビュー機能**
   - リアルタイムプレビュー（iframe内）
   - 「保存してPDF生成」ボタン

### UI/UX設計
- **レスポンシブデザイン**: スマホ・タブレット・PCで最適表示
- **直感的な操作**: ドラッグ&ドロップ、モーダルダイアログ
- **リアルタイムフィードバック**: 編集中にプレビュー更新
- **ローディング表示**: PDF生成中のスピナー表示

## 🤖 LLM文章生成機能

### 使用するAPI
- OpenAI GPT-4 / GPT-3.5-turbo
- または Anthropic Claude

### 生成シナリオ

#### 1. プロフィール文章生成
**入力情報**:
- 名前
- 生年月日
- 出身地
- 職業
- 趣味

**プロンプト例**:
```
以下の情報から、自分史のプロフィール文章を生成してください。
親しみやすく、読みやすい文章でお願いします。

名前: {name}
生年月日: {birthDate}
出身地: {birthPlace}
職業: {occupation}
趣味: {hobbies}

200文字程度でお願いします。
```

#### 2. 年表説明文生成
**入力情報**:
- 年
- タイトル
- （既存の説明文があれば）

**プロンプト例**:
```
自分史の年表で、以下の出来事についての説明文を生成してください。
当時の気持ちや状況を想像して、温かみのある文章でお願いします。

年: {year}
出来事: {title}

100〜150文字程度でお願いします。
```

#### 3. チャプター文章生成（将来的に）
**入力情報**:
- チャプタータイトル
- 関連する年表項目
- キーワード

## 🏗️ 技術スタック

### バックエンド
- **Python**: FastAPI
- **LINE Messaging API**: メッセージ送受信
- **LINE LIFF**: 編集画面のWebView
- **OpenAI API**: 文章生成
- **Auto-Designer API**: PDF生成（Vivliostyle）

### フロントエンド（LIFF編集画面）
- **HTML5 / CSS3**
- **JavaScript（Vanilla or Vue.js）**
- **LINE LIFF SDK**: LINEとの連携
- **Axios**: API通信
- **SortableJS**: ドラッグ&ドロップ
- **Tailwind CSS**: スタイリング

### ストレージ
- **ローカルファイルシステム**: 画像・PDF保存
- **メモリストレージ**: セッション管理（将来的にはRedis）

## 📡 API設計

### 1. 簡易PDF生成エンドポイント
```
POST /api/memoir/quick-create
Content-Type: application/json

Request:
{
  "user_id": "U1234567890",
  "title": "私の人生物語",
  "cover_image_url": "https://example.com/uploads/cover.jpg"
}

Response:
{
  "success": true,
  "pdf_url": "https://example.com/uploads/memoir_xxx.pdf",
  "edit_url": "https://liff.line.me/{liff_id}?session_id=xxx",
  "session_id": "session_xxx"
}
```

### 2. 編集データ取得
```
GET /api/memoir/edit/{session_id}

Response:
{
  "session_id": "session_xxx",
  "user_id": "U1234567890",
  "data": {
    "title": "私の人生物語",
    "subtitle": "〜これまでの道のり〜",
    "author": "あなた",
    "cover_image_url": "...",
    "profile": {
      "description": "",
      "birthDate": "",
      "birthPlace": "",
      "occupation": "",
      "hobbies": []
    },
    "timeline": []
  }
}
```

### 3. 編集データ保存＆PDF再生成
```
POST /api/memoir/save/{session_id}
Content-Type: application/json

Request:
{
  "data": {
    "title": "私の人生物語",
    "subtitle": "〜これまでの道のり〜",
    "author": "鈴木太郎",
    "cover_image_url": "...",
    "profile": {...},
    "timeline": [...]
  }
}

Response:
{
  "success": true,
  "pdf_url": "https://example.com/uploads/memoir_xxx_v2.pdf",
  "message": "PDFを更新しました"
}
```

### 4. LLM文章生成
```
POST /api/memoir/generate-text
Content-Type: application/json

Request:
{
  "type": "profile",  // "profile" | "timeline_description"
  "data": {
    "name": "鈴木太郎",
    "birthDate": "1985年3月15日",
    ...
  }
}

Response:
{
  "success": true,
  "generated_text": "鈴木太郎は1985年3月15日、東京で生まれました。..."
}
```

### 5. 画像アップロード
```
POST /api/memoir/upload-image/{session_id}
Content-Type: multipart/form-data

Request:
- file: [画像ファイル]

Response:
{
  "success": true,
  "image_url": "https://example.com/uploads/image_xxx.jpg",
  "file_id": "file_xxx"
}
```

## 🎮 編集画面の配信方法

### シンプルなアプローチ（Phase 1）
1. **静的HTMLファイル**として作成
   - ファイル: `/liff/edit.html`
   - CSS・JSは同じファイル内に記述（またはインライン）
   
2. **FastAPIで配信**
   ```python
   app.mount("/liff", StaticFiles(directory="liff"), name="liff")
   ```

3. **URL構造**
   - 編集画面: `https://your-domain.com/liff/edit.html?session_id={session_id}`
   - セッションIDをURLパラメータで渡す

4. **認証**
   - セッションIDとユーザーIDの紐付けをバックエンドで管理
   - LIFF SDK は後から追加可能（オプション）

### LIFF化（Phase 2 - オプション）
後から必要になったら、LIFF（LINE Front-end Framework）に移行可能：
- **LIFF ID登録**: LINE Developersコンソールで設定
- **liff.js追加**: ユーザー情報取得、メッセージ送信などの機能
- **エンドポイントURL**: `https://your-domain.com/liff/edit.html`

## 📦 データ構造

### QuickMemoirSession
```python
@dataclass
class QuickMemoirSession:
    session_id: str
    user_id: str
    state: str  # "waiting_title" | "waiting_cover" | "editing" | "completed"
    data: MemoirData
    cover_image_url: Optional[str]
    created_at: datetime
    updated_at: datetime
```

### MemoirData
```python
@dataclass
class MemoirData:
    title: str
    subtitle: str = "〜これまでの道のり〜"
    author: str = "あなた"
    date: str = ""
    cover_image_url: Optional[str] = None
    profile: Dict[str, Any] = None
    timeline: List[Dict[str, Any]] = None
    template: str = "modern-vertical-cover"
```

## 🚀 実装フェーズ

### Phase 1: MVP（最小実装）✅ 実装完了
- [x] 簡易フローサービス作成（タイトル + カバー写真 → PDF）
- [x] LIFF編集画面の基本実装（テキスト編集のみ）
- [x] 編集データ保存＆PDF再生成
- [x] LINE Bot統合
- [x] **2025-10-25**: 入口を「作成」キーワードに統一

### Phase 2: LLM文章生成機能
- [ ] OpenAI API統合
- [ ] プロフィール文章生成
- [ ] 年表説明文生成
- [ ] 生成文章の編集・調整UI

### Phase 3: 高度な編集機能
- [ ] 画像アップロード・管理
- [ ] ドラッグ&ドロップによる並び替え
- [ ] テンプレート選択・プレビュー
- [ ] リアルタイムプレビュー

### Phase 4: UX改善
- [ ] 音声入力対応（録音 → STT → テキスト）
- [ ] 画像の自動最適化・トリミング
- [ ] 多言語対応
- [ ] PDFダウンロード・共有機能

## 📝 実装の詳細（2025-10-25更新）

### 入口の統一

**変更内容**:
- すべてのフローの入口を「作成」キーワードに統一
- 写真自分史・従来自分史の直接トリガーを削除
- セッション外でのメディアファイル送信による直接開始を削除

**削除されたトリガー**:
1. **写真自分史**: `['写真で作る', '写真自分史', 'フォト']`
2. **従来自分史**: `['自分史作成', 'memoir', '自分史', '人生の歩み']`

**削除されたハンドラー**:
- 動画メッセージハンドラー（`handle_video_message`）
- 音声メッセージハンドラー（`handle_audio_message`）
- ファイルメッセージハンドラー（`handle_file_message`）

**保持された機能**:
- 簡易フロー内での画像処理（カバー写真アップロード）
- 写真フローのセッション継続処理
- テキストメッセージによる対話フロー

**ユーザー体験**:
- セッション外で画像を送信: 「画像を受信しました。自分史を作成する場合は「作成」と送信してください。」
- セッション外でテキストを送信: 「自分史を作成する場合は「作成」と送信してください。」
- 動画・音声・ファイル送信: 処理されない（ハンドラー削除）
- 統一された入口: 「作る」「作成」「つくる」のみ
- ChatGPT応答: 削除（フリーテキストへの応答なし）

**技術的な変更**:
- `photo_memoir_service.py`: `is_photo_memoir_request()`メソッド削除
- `memoir_service.py`: `is_memoir_request()`メソッド削除
- `line_service.py`: 
  - 写真自分史の直接トリガー判定削除
  - 従来自分史の全フロー削除
  - VideoMessage、AudioMessage、FileMessageContentのインポート削除
  - 画像メッセージ処理の簡素化
  - `handle_chatgpt_response()`関数削除
  - `get_chatgpt_response`のインポート削除
  - フリーテキストへの応答を案内メッセージに変更

## 🔐 セキュリティ考慮事項

1. **セッション管理**
   - セッションIDは UUID v4 で生成
   - セッションの有効期限: 24時間
   - セッションとユーザーIDの紐付けチェック

2. **画像アップロード**
   - ファイルサイズ制限: 10MB
   - 許可する拡張子: jpg, jpeg, png, gif
   - ファイル名のサニタイズ

3. **LIFF認証**
   - LIFF SDK経由でユーザーIDを取得
   - セッションIDとユーザーIDの一致確認

## 📊 メトリクス・分析

### 追跡する指標
- **コンバージョン率**
  - トリガーワード → タイトル入力
  - タイトル入力 → カバー写真アップロード
  - カバー写真 → PDF生成完了
  - PDF生成 → 編集画面オープン
  - 編集画面 → 保存・再生成

- **平均時間**
  - 開始 → 初回PDF生成までの時間
  - 編集画面滞在時間
  - 保存 → PDF再生成の時間

- **機能利用率**
  - LLM文章生成の利用回数
  - 画像アップロード数
  - テンプレート変更回数

## 🐛 エラーハンドリング

### エラーシナリオと対応

1. **PDF生成失敗**
   - リトライ（最大3回）
   - エラーメッセージをユーザーに通知
   - セッション状態を維持

2. **画像アップロード失敗**
   - ファイルサイズ確認
   - フォーマット確認
   - リトライ提案

3. **LLM生成失敗**
   - タイムアウト設定（30秒）
   - デフォルトテキスト表示
   - 再生成ボタン提供

4. **セッション期限切れ**
   - 再作成を促すメッセージ
   - 可能であればデータ復元

## 🚨 現在の課題と改善案

### 現在の実装（フォームベース編集）の問題点

#### 1. **テンプレートと編集フォームの乖離**
- **問題**: `edit.html` のフォームフィールドが固定されている
  - プロフィール項目（生年月日、出身地、職業、趣味）
  - 年表項目（年、タイトル、説明文）
- **影響**: テンプレートに該当する項目がない場合、入力しても反映されない
- **例**: 「好きな食べ物」「座右の銘」などを追加したくてもテンプレートに対応箇所がない

#### 2. **ユーザーの入力負担が大きい**
- **問題**: フォームの空欄を埋める作業が心理的ハードルになる
- **影響**: 
  - 編集画面を開いても何も入力せずに閉じてしまう
  - 「後で入力しよう」と思って忘れてしまう
  - 文章を考えるのが面倒で途中で諦める

#### 3. **AI文章生成の使いづらさ**
- **問題**: 先に項目を埋めてから「AI生成」ボタンを押す必要がある
- **影響**: 
  - 「AIが書いてくれる」のに、まず自分で情報を入力する矛盾
  - 生成された文章が意図と違っても、再生成しづらい

#### 4. **写真の魅力が活かせていない**
- **問題**: カバー写真1枚のみで、他の写真を追加する導線がない
- **影響**: 
  - 視覚的な魅力に欠ける
  - 写真を見せることで記憶が蘇る体験がない
  - 「自分史 = 文章」という固定観念から抜け出せない

### 💡 新しいアプローチ: 写真中心・対話ベース自分史

#### コンセプト
**「写真を見ながら、AIと対話するだけで自分史が完成」**

- ✅ 写真が主役
- ✅ フォーム入力不要
- ✅ 会話で完結（テキスト・音声両対応）
- ✅ AIが質問→回答→ストーリー生成
- ✅ 柔軟な構造（写真に応じて動的に調整）

#### 新フロー

```
👤 ユーザー: 「自分史作る」
🤖 Bot: 「写真を送ってください（複数枚OK）📸」
     「送り終わったら「完了」と送信してください」

👤 ユーザー: [写真1] [写真2] [写真3] ... [写真N]
👤 ユーザー: 「完了」

🤖 Bot: 「写真を{N}枚受け取りました！」
     「これから写真について質問するので、答えてください」
     「テキストでも音声でも大丈夫です🎤」
     
     [写真1を表示]
     「この写真について教えてください」
     
     質問カルーセル:
     ・いつ頃の写真ですか？
     ・どこで撮った写真ですか？
     ・この時の思い出を教えてください

👤 ユーザー: 「2015年春、桜の下で家族と撮りました。
          子供が生まれて初めてのお花見で...」
     または
     [音声メッセージ]

🤖 Bot: 「素敵な思い出ですね✨」
     「AIが文章をまとめています...」
     
     「こんな感じでまとめました：
     『2015年春、満開の桜の下で家族と過ごした特別な日。
     子供が生まれて初めてのお花見は、新しい命の誕生を
     祝福するような穏やかな時間だった。』」
     
     「このままでOKですか？」
     👍 いいね / ✏️ 修正 / 🔄 再生成

👤 ユーザー: 👍

🤖 Bot: [写真2を表示]
     「次の写真です」
     「この写真について教えてください」
     ...

[全写真の対話完了]

🤖 Bot: 「すべての写真のストーリーが完成しました！」
     「PDFを生成しています...⏳」
     
🤖 Bot: ✨ 完成しました！
     📄 PDFを見る
     ✏️ 内容を修正
     📸 写真を追加
```

#### 技術仕様

##### 1. 写真収集フェーズ

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
    # AI質問セッション
    questions: List[Dict[str, str]] = field(default_factory=list)
    answers: List[str] = field(default_factory=list)
    # 生成されたストーリー
    generated_story: Optional[str] = None
    story_approved: bool = False
    # メタデータ（AIが推測）
    estimated_date: Optional[str] = None
    estimated_location: Optional[str] = None
    tags: List[str] = field(default_factory=list)
```

##### 2. AI質問生成

```python
def generate_photo_questions(photo_index: int, total_photos: int, context: dict) -> List[str]:
    """
    写真に対する質問を生成
    
    Args:
        photo_index: 現在の写真インデックス
        total_photos: 総写真数
        context: 前の写真の情報（時系列推測に使用）
    
    Returns:
        質問リスト（3-5個）
    """
    # Vision APIで写真の内容を分析（オプション）
    # 写真の内容に応じて質問を動的に生成
    
    base_questions = [
        "いつ頃の写真ですか？（例：2015年春、10年前、子供の頃）",
        "どこで撮った写真ですか？",
        "誰が写っていますか？",
        "この時の思い出やエピソードを教えてください",
    ]
    
    # 写真の分析結果に応じて追加質問
    # 例: 人物が写っている → "この人との関係は？"
    # 例: 風景写真 → "なぜこの場所を訪れたのですか？"
    
    return base_questions
```

##### 3. ストーリー生成

```python
def generate_photo_story(photo: PhotoItem, answers: List[str]) -> str:
    """
    回答からストーリーを生成
    
    Args:
        photo: 写真情報
        answers: ユーザーの回答リスト
    
    Returns:
        生成されたストーリー（100-200文字）
    """
    prompt = f"""
    ユーザーが写真について以下のように答えました。
    これを感動的で読みやすい自分史のストーリーにまとめてください。
    
    回答:
    {chr(10).join(f'- {a}' for a in answers)}
    
    要件:
    - 100〜200文字程度
    - 情緒的で温かみのある文章
    - 時期・場所・人物・出来事を自然に盛り込む
    - 読者が情景を想像できる表現
    """
    
    return openai_service.generate_text(prompt)
```

##### 4. 音声対応

```python
async def handle_audio_response(audio_file: bytes) -> str:
    """
    音声メッセージをテキストに変換
    
    Args:
        audio_file: 音声ファイル（m4a, mp3等）
    
    Returns:
        テキスト変換結果
    """
    # OpenAI Whisper API使用
    transcription = await openai_service.transcribe_audio(audio_file)
    return transcription.text
```

##### 5. 動的PDFレイアウト

```python
def generate_photo_memoir_pdf(session: PhotoMemoirSession) -> bytes:
    """
    写真中心の自分史PDFを生成
    
    レイアウト:
    - 1ページ = 1写真 + ストーリー
    - 写真が主役（70%）、テキストは補助（30%）
    - 時系列順に自動ソート
    """
    template_data = {
        "pages": []
    }
    
    # 時系列順にソート
    sorted_photos = sort_photos_by_date(session.photos)
    
    for photo in sorted_photos:
        page = {
            "image": photo.photo_url,
            "date": photo.estimated_date or "",
            "location": photo.estimated_location or "",
            "story": photo.generated_story,
            "layout": "photo-primary"  # 写真メインレイアウト
        }
        template_data["pages"].append(page)
    
    return vivliostyle_service.generate_pdf(
        template_name="photo-memoir",
        data=template_data
    )
```

#### 実装フェーズ

##### Phase 1: 写真収集 & 基本対話 🎯 次に実装
- [ ] `PhotoMemoirService` 作成
- [ ] 写真収集フロー（複数枚対応）
- [ ] 基本的な質問生成（固定質問）
- [ ] テキスト回答の処理
- [ ] シンプルなストーリー生成
- [ ] 1写真1ページの基本PDF生成

##### Phase 2: AI質問 & 音声対応
- [ ] 写真内容分析（Vision API）
- [ ] 動的質問生成（写真内容に応じた質問）
- [ ] 音声メッセージ対応（Whisper API）
- [ ] ストーリーの承認・修正・再生成フロー

##### Phase 3: 高度な機能
- [ ] 時系列自動推測
- [ ] 写真の追加・削除・並び替え
- [ ] テンプレート選択（写真メイン、テキストメイン、バランス型）
- [ ] カバー自動生成（ベスト写真選択）

##### Phase 4: UX改善
- [ ] プログレスバー（「5枚中3枚目」）
- [ ] スキップ機能（詳しく書きたくない写真）
- [ ] バッチ質問（複数写真を一度に説明）
- [ ] 家族・友人からのコメント機能

#### メリット

1. **入力負担の大幅削減**
   - フォーム項目を埋める必要なし
   - 会話形式で自然に情報を引き出せる

2. **写真が主役**
   - 視覚的に魅力的
   - 写真を見ることで記憶が蘇りやすい

3. **柔軟な構造**
   - 写真の枚数に制限なし
   - 各写真に対する情報量も自由
   - テンプレートに縛られない

4. **AI活用の最大化**
   - 質問生成
   - 回答からストーリー生成
   - 写真分析
   - 音声→テキスト変換

5. **完成度の高さ**
   - AIが文章を整えるため、誰でも美しい自分史
   - 写真とストーリーの組み合わせで感動的

#### デメリットと対策

| デメリット | 対策 |
|----------|------|
| 対話が長くなる | バッチ質問機能、スキップ機能 |
| 音声入力のエラー | テキスト修正機能 |
| 写真が多いと疲れる | 途中保存、後で再開機能 |
| AI生成の精度 | 承認・修正・再生成フロー |

## 📝 今後の拡張アイデア

1. **テンプレートマーケットプレイス**
   - ユーザーがテンプレートをシェア
   - 人気テンプレートランキング

2. **AIコーチング機能** ✅ 写真対話フローで実現
   - 「次は幼少期の思い出を書いてみませんか？」
   - 質問に答える形式で自動的に年表を埋める

3. **コラボレーション機能**
   - 家族・友人から思い出を募集
   - コメント機能

4. **印刷注文連携**
   - Raksul等の印刷サービスと連携
   - ボタン一つで製本注文

5. **SNSシェア**
   - PDF一部をプレビュー画像として生成
   - Twitter, Facebook等でシェア

## 🛠️ 技術的な改善履歴

### 2025-10-25: パフォーマンスとUX改善

#### 1. イベントループの問題修正
**問題**: 編集画面からの保存時に「Cannot run the event loop while another loop is running」エラーが発生

**解決策**:
- `quick_memoir_service.generate_quick_pdf()` を `async def` に変更
- 既存のイベントループを使用（ネストしたループを作成しない）
- API層では `await generate_quick_pdf()`、スレッド内では `asyncio.run()` を使用

```python
# quick_memoir_service.py
async def generate_quick_pdf(self, session, vivliostyle_options=None):
    await vivliostyle_service.generate_pdf(...)

# routes.py (async関数内)
pdf_result = await quick_memoir_service.generate_quick_pdf(session)

# line_service.py (スレッド内)
pdf_result = asyncio.run(quick_memoir_service.generate_quick_pdf(session))
```

#### 2. 画像URLの永続化とセッション管理
**問題**: 編集画面で保存すると、画像URLが失われてPDFに画像が含まれなくなる

**解決策**: Single Source of Truth（単一情報源）原則を適用
- サーバー側のセッションデータを唯一の真の情報源に
- 編集画面からは編集可能な項目のみ送信（テキスト、プロフィールなど）
- 画像URLはセッションに保持され、年番号でマッチング

```python
def update_memoir_data(self, session_id: str, data: Dict[str, Any]) -> bool:
    # 既存の画像URLをyearでマッチング
    existing_images = {item.get("year"): item["image"] 
                      for item in session.data.timeline 
                      if "image" in item}
    
    # 新しいデータに画像URLをマージ
    for item in data["timeline"]:
        year = item.get("year")
        if year in existing_images and "image" not in item:
            item["image"] = existing_images[year]
```

**メリット**:
- データの整合性が保証される
- クライアント側の複雑さが削減
- 画像URLがサーバー側で確実に保持される

#### 3. ローカル画像処理の最適化
**問題**: 画像URLがローカルメディアファイル（`/media/image/...`）の場合、HTTPダウンロードでタイムアウト（30秒）

**解決策**: ローカルファイルを直接コピー
```python
# vivliostyle_service.py
async def _process_image(self, image_path, temp_dir, prefix="image"):
    if "/media/image/" in image_path or "/media/file/" in image_path:
        # file_idを抽出
        file_id = image_path.split("/media/")[-1].split("/")[-1]
        
        # file_serviceでローカルパスを取得
        file_metadata = file_service.get_file_by_id(file_id)
        source_path = uploads_dir / file_metadata['stored_filename']
        
        # 直接コピー（HTTPダウンロード不要）
        shutil.copy2(source_path, dest_path)
        return dest_path.name
```

**結果**:
- 処理時間: **30秒以上 → 3秒** に短縮（10倍高速化）
- タイムアウトエラーなし
- 画像が確実にPDFに含まれる

#### 4. Flex Messageの色改善
**問題**: 蛍光色が強く、目に優しくない

**解決策**: 落ち着いた色に変更
- 紫色: `#667eea` → `#6366F1`（インディゴ）
- 緑色: `#38ef7d` → `#10B981`（エメラルドグリーン）

**適用箇所**:
- LINE メッセージ（Flex Message）
- LIFF編集画面のUI

#### 5. 更新完了Flex Message追加
**問題**: 編集後の保存時、テキストメッセージのみで視覚的に地味

**解決策**: 更新完了用のFlex Messageを追加
- ヘッダー色: 緑（`#10B981`）で「更新」を強調
- 「✨ 更新完了！」タイトル
- 「📄 PDFを見る」「✏️ さらに編集」ボタン

### パフォーマンス比較

| 項目 | 改善前 | 改善後 | 改善率 |
|------|--------|--------|--------|
| 画像処理 | 30秒以上（タイムアウト） | 3秒 | 10倍高速化 |
| イベントループエラー | 頻発 | なし | 100%解消 |
| 画像の永続性 | 編集後に消失 | 確実に保持 | 100%改善 |

## 🔗 関連ドキュメント

- [Vivliostyle テンプレート](../../vivliostyle/sample/templates/modern/)
- [LINE Messaging API ドキュメント](https://developers.line.biz/ja/docs/messaging-api/)
- [LINE LIFF ドキュメント](https://developers.line.biz/ja/docs/liff/)
- [簡易フロー実装ガイド](./quick-flow-guide.md)
- [Vivliostyle統合ガイド](./vivliostyle-integration.md)
- [トラブルシューティング](./troubleshooting-vivliostyle.md)
- [OpenAI API ドキュメント](https://platform.openai.com/docs/)
