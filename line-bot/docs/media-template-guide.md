# メディアテンプレート - 実装ガイド

## 🎯 概要

**メディアテンプレート**は、構造化されたページ構成を持つ自分史作成の新しいアプローチです。テンプレートスキーマに基づいて、ユーザーから情報を順番に収集し、デザイン性の高いPDFを生成します。

### 従来のアプローチとの違い

| 項目 | 従来（簡易フロー） | メディアテンプレート |
|------|-------------------|---------------------|
| ページ構成 | 自由（ユーザー任せ） | テンプレートで定義 |
| データ収集 | タイトル+カバー写真のみ | スキーマ駆動で順番に収集 |
| ページ数 | 可変（後から編集） | 固定+拡張可能 |
| デザイン | シンプル | 複数のページ型を組み合わせ |

## 📋 テンプレートスキーマ

### 自分史_縦書き（memoir_vertical）

現在実装されているテンプレートです。

#### ページ構成

1. **表紙（title_page）** - 1ページ
   - タイトル（テキスト）
   - 著者名（テキスト）
   - カバー写真（画像）

2. **見開きページ（spread_1）** - 2-3ページ
   - 左ページ: 画像フルサイズ
   - 右ページ: 縦書き3段組みテキスト
   - ストーリータイトル（テキスト、任意）
   - ストーリー本文（テキスト、最大2000文字）

3. **単一ページ（single_1）** - 4ページ
   - 画像+縦書きテキスト
   - セクションタイトル（テキスト、任意）
   - 説明文（テキスト、最大500文字）

**合計**: 4ページ

## 🔄 フロー

### ユーザー体験

```
👤 ユーザー: 「作る」「作成」（トリガーワード）
   ↓
🤖 Bot: 【1/6】
     📄 表紙
     
     ✍️ 自分史のタイトル
     （例：私の人生物語）
   ↓
👤 ユーザー: 「私の人生物語」
   ↓
🤖 Bot: 【2/6】
     📄 表紙
     
     ✍️ 著者名
     （例：鈴木太郎）
   ↓
👤 ユーザー: 「鈴木太郎」
   ↓
🤖 Bot: 【3/6】
     📄 表紙
     
     📸 カバー写真（縦長推奨）
     写真を送ってください。
   ↓
👤 ユーザー: [写真送信]
   ↓
🤖 Bot: 【4/6】
     📄 見開きページ（画像+縦書き）
     
     📸 見開きページ用の写真（縦長推奨）
     写真を送ってください。
   ↓
👤 ユーザー: [写真送信]
   ↓
🤖 Bot: 【5/6】
     📄 見開きページ（画像+縦書き）
     
     ✍️ 縦書きのストーリー本文
     （この時期の思い出やエピソードを書いてください）
   ↓
👤 ユーザー: 「幼少期の思い出です...」（長文OK）
   ↓
🤖 Bot: 【6/6】
     📄 単一ページ（画像+テキスト）
     
     📸 ページ用の写真
     写真を送ってください。
   ↓
👤 ユーザー: [写真送信]
   ↓
🤖 Bot: ✨ すべての情報を受け取りました！
     PDFを生成しています...⏳
   ↓ (3〜5秒)
🤖 Bot: ✨ 自分史が完成しました！
     📄 PDF: [URL]
     ファイル名: memoir_vertical_20251025_120000.pdf
     サイズ: 1,234,567 bytes
```

### プログレス表示

各フィールドで「【現在/総数】」のプログレスを表示：
- 総数 = すべてのページのフィールド数の合計
- 例: 表紙（3フィールド）+ 見開き（2フィールド）+ 単一（1フィールド）= 6フィールド

## 🏗️ アーキテクチャ

### データフロー

```
1. ユーザー入力
   ↓
2. media_memoir_service.process_user_input()
   ├─ フィールドタイプ検証（text/image）
   ├─ データ保存（PageData）
   └─ 次のフィールドプロンプト生成
   ↓
3. すべてのフィールド収集完了
   ↓
4. media_memoir_service.generate_pdf()
   ├─ テンプレートデータ準備
   ├─ Jinja2レンダリング（templates/media/memoir-vertical/template.html）
   └─ Vivliostyle CLI実行
   ↓
5. PDF生成完了 → ユーザーに送信
```

### ファイル構成

```
line-bot/
├── app/
│   └── services/
│       ├── media_template_schema.py    # スキーマ定義
│       ├── media_memoir_service.py     # メディアフロー管理
│       └── line_service.py             # LINEハンドラー
└── templates/
    └── media/
        └── memoir-vertical/
            └── template.html            # Jinja2テンプレート
```

## 📦 データ構造

### MediaTemplateSchema

```python
@dataclass
class MediaTemplateSchema:
    template_id: str              # "memoir_vertical"
    template_name: str            # "自分史_縦書き"
    writing_mode: WritingMode     # VERTICAL
    description: str              # テンプレートの説明
    pages: List[PageSchema]       # ページ構成
    category: str                 # "memoir"
```

### PageSchema

```python
@dataclass
class PageSchema:
    page_id: str                  # "title_page", "spread_1", "single_1"
    page_type: PageType           # TITLE, SPREAD_IMAGE_TEXT, SINGLE_IMAGE_TEXT
    page_number: int              # ページ番号
    display_name: str             # "表紙", "見開きページ"
    description: str              # ページの説明
    fields: List[PageFieldSchema] # フィールド定義
    template_path: str            # Vivliostyleテンプレートパス（未使用）
    is_deletable: bool            # 削除可能か（将来的な機能）
    is_duplicatable: bool         # 複製可能か（将来的な機能）
```

### PageFieldSchema

```python
@dataclass
class PageFieldSchema:
    field_name: str               # "title", "author", "cover_image"
    field_type: str               # "text" | "image"
    required: bool                # 必須かどうか
    default_value: Any            # デフォルト値
    description: str              # フィールドの説明
    max_length: Optional[int]     # テキストの最大文字数
    placeholder: str              # プレースホルダー
```

### MediaMemoirSession

```python
@dataclass
class MediaMemoirSession:
    session_id: str               # "media_abc123"
    user_id: str                  # LINE user ID
    template_id: str              # "memoir_vertical"
    state: str                    # "collecting" | "editing" | "completed"
    current_field_index: int      # 現在収集中のフィールドインデックス
    pages: List[PageData]         # ページデータ
    created_at: datetime
    updated_at: datetime
```

### PageData

```python
@dataclass
class PageData:
    page_id: str                  # "title_page"
    page_type: str                # "title"
    page_number: int              # 1
    data: Dict[str, Any]          # {"title": "...", "author": "...", "cover_image": "..."}
```

## 🎨 テンプレート（Jinja2）

### templates/media/memoir-vertical/template.html

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <style>
        /* タイトルページスタイル */
        .title-page { ... }
        
        /* 見開きページスタイル */
        .spread { ... }
        
        /* 単一ページスタイル */
        .single-page { ... }
    </style>
</head>
<body>
    {% for page in pages %}
        {% if page.page_type == "title" %}
            {# タイトルページ #}
            <div class="title-page">...</div>
            
        {% elif page.page_type == "spread_image_text" %}
            {# 見開き画像+縦書きテキスト #}
            <div class="spread">...</div>
            
        {% elif page.page_type == "single_image_text" %}
            {# 単一ページ画像+テキスト #}
            <div class="single-page">...</div>
        {% endif %}
    {% endfor %}
</body>
</html>
```

### テンプレートデータ

```python
{
    "title": "私の人生物語",
    "pages": [
        {
            "page_type": "title",
            "page_number": 1,
            "data": {
                "title": "私の人生物語",
                "author": "鈴木太郎",
                "cover_image": "/media/image/abc123"
            }
        },
        {
            "page_type": "spread_image_text",
            "page_number": 2,
            "data": {
                "image": "/media/image/def456",
                "story_title": "幼少期の思い出",
                "story_text": "..."
            }
        },
        {
            "page_type": "single_image_text",
            "page_number": 4,
            "data": {
                "image": "/media/image/ghi789",
                "section_title": "学生時代",
                "description": "..."
            }
        }
    ]
}
```

## 🚀 新しいテンプレートの追加方法

### 1. スキーマ定義を追加

`app/services/media_template_schema.py`:

```python
# 新しいテンプレート定義
TRAVEL_HORIZONTAL_TEMPLATE = MediaTemplateSchema(
    template_id="travel_horizontal",
    template_name="旅ログ_横書き",
    writing_mode=WritingMode.HORIZONTAL,
    description="横書きの旅行記録スタイル",
    category="travel",
    pages=[
        # ページ定義
    ]
)

# レジストリに登録
TEMPLATE_REGISTRY: Dict[str, MediaTemplateSchema] = {
    "memoir_vertical": MEMOIR_VERTICAL_TEMPLATE,
    "travel_horizontal": TRAVEL_HORIZONTAL_TEMPLATE,  # 追加
}
```

### 2. Jinja2テンプレートを作成

`templates/media/travel-horizontal/template.html`:

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <style>
        /* 旅ログ用スタイル */
    </style>
</head>
<body>
    {% for page in pages %}
        {# ページタイプに応じた表示 #}
    {% endfor %}
</body>
</html>
```

### 3. フローに統合

`app/services/line_service.py`:

```python
# トリガーワードで判定
if '旅' in user_message or 'travel' in user_message:
    session, response = media_memoir_service.start_media_memoir(user_id, "travel_horizontal")
```

## 🔧 カスタマイズ

### フィールドの追加

スキーマに新しいフィールドを追加：

```python
PageFieldSchema(
    field_name="birth_date",
    field_type="text",
    required=False,
    description="生年月日",
    max_length=20,
    placeholder="例：1985年3月15日"
)
```

### ページの追加

スキーマに新しいページを追加：

```python
PageSchema(
    page_id="gallery_1",
    page_type=PageType.SINGLE_TEXT_ONLY,
    page_number=5,
    display_name="ギャラリー",
    description="写真ギャラリーページ",
    template_path="single/photo-gallery",
    is_deletable=True,
    is_duplicatable=True,
    fields=[...]
)
```

### バリデーション

`media_memoir_service.py`に検証ロジックを追加：

```python
def validate_field(self, field_schema, value):
    if field_schema.max_length and len(value) > field_schema.max_length:
        raise ValueError(f"文字数が上限を超えています（{field_schema.max_length}文字以内）")
    return True
```

## 📊 メトリクス

### 追跡する指標

- **コンバージョン率**: 各フィールドでの離脱率
- **平均時間**: 各フィールドの入力時間
- **テンプレート選択率**: どのテンプレートが人気か
- **完成率**: 最後までPDF生成に至った割合

## 🐛 トラブルシューティング

### PDF生成に失敗する

1. テンプレートパスを確認: `templates/media/{template_id}/template.html`
2. データ構造を確認: すべての必須フィールドが埋まっているか
3. 画像URLを確認: ローカルファイルが存在するか

### フィールドがスキップされる

1. `current_field_index`が正しくインクリメントされているか確認
2. `_get_current_field()`のロジックを確認

### 画像が表示されない

1. `vivliostyle_service.py`の`_process_image()`を確認
2. ローカルファイルが正しくコピーされているか確認

## 🎯 今後の拡張

### Phase 2: ページ追加・削除機能

```python
# ページの追加
media_memoir_service.add_page(
    session_id="media_abc123",
    page_type="single_image_text",
    insert_after="spread_1"
)

# ページの削除（is_deletable=Trueの場合のみ）
media_memoir_service.delete_page(
    session_id="media_abc123",
    page_id="single_1"
)
```

### Phase 3: AI文章生成統合

```python
# ストーリー本文の自動生成
story = openai_service.generate_memoir_text(
    context={"title": "幼少期の思い出", "keywords": ["家族", "夏休み"]},
    max_length=500
)
```

### Phase 4: 編集画面

LIFF編集画面でページごとの編集：
- ページの並び替え
- フィールドの編集
- プレビュー機能

## 📚 関連ドキュメント

- [設計ドキュメント](./design.md)
- [簡易フロー実装ガイド](./quick-flow-guide.md)
- [Vivliostyle統合ガイド](./vivliostyle-integration.md)

## 🎊 まとめ

メディアテンプレートは、構造化されたアプローチで美しいPDFを生成する新しい方法です。

**メリット**:
- ✅ デザイン性の高いPDF
- ✅ スキーマ駆動で拡張しやすい
- ✅ ユーザーに必要な情報を順番に収集
- ✅ 複数のページ型を組み合わせ可能

**次のステップ**:
1. 他のメディアタイプを追加（旅ログ、推しログなど）
2. ページ追加・削除機能の実装
3. AI文章生成の統合
4. LIFF編集画面の作成

楽しい自分史作成体験をお楽しみください！✨

