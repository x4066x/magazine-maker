# 雑誌風PDF自動生成サービス

FastAPI + Vivliostyle CLIを使用して雑誌風PDFを自動生成するサービスです。

## 機能

- 複数のテンプレート（タイトルページ、見開きページ、片面ページ）
- サンプル画像を使用したPDF生成
- RESTful API
- 非同期処理
- 自動クリーンアップ

## ディレクトリ構成

```
vivliostyle/
├── app/                    # FastAPIアプリケーション
│   ├── main.py            # エントリーポイント
│   ├── pdf_service.py     # PDF生成ロジック
│   ├── schemas.py         # Pydanticスキーマ
│   └── settings.py        # 設定管理
├── sample/
│   ├── images/            # サンプル画像
│   └── templates/         # HTML/CSSテンプレート
│       ├── title/         # タイトルページ
│       ├── spread/        # 見開きページ
│       └── single/        # 片面ページ
├── docs/                  # 設計ドキュメント
├── requirements.txt       # Python依存関係
└── test_pdf_generation.py # テストスクリプト
```

## セットアップ

### 1. 依存関係のインストール

```bash
# uvを使用して依存関係をインストール
uv sync

# または個別にインストール
uv add fastapi uvicorn jinja2 pydantic python-multipart aiofiles

# Vivliostyle CLI
npm install -g vivliostyle-cli
```

### 2. 動作確認

```bash
# アプリケーションの読み込みテスト
uv run python -c "from app.main import app; print('FastAPI app loaded successfully')"

# PDF生成テスト
uv run python test_pdf_generation.py
```

### 3. サーバー起動（開発中）

```bash
# 開発サーバー（ポート8000が使用中の場合は8001を使用）
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# または
uv run python -m app.main
```

### 4. ヘルスチェック

```bash
curl http://localhost:8001/health
```

## 実装状況

### ✅ 完了項目
- [x] FastAPIアプリケーション基盤
- [x] PDF生成サービス（PDFService）
- [x] Pydanticスキーマ定義
- [x] 設定管理（Settings）
- [x] タイトルページテンプレート
- [x] 引用文見開きページテンプレート
- [x] 画像+テキスト片面ページテンプレート
- [x] サンプル画像処理
- [x] テストスクリプト
- [x] エラーハンドリング
- [x] ログ機能
- [x] 自動クリーンアップ
- [x] Vivliostyle CLI連携
- [x] PDF生成テスト（成功）

### 🔄 開発中・未完了項目
- [ ] Webサーバー起動の安定化
- [ ] APIエンドポイントの動作確認
- [ ] 残りのテンプレート実装
- [ ] エラーハンドリングの改善

## 使用方法

### 現在利用可能な機能

#### PDF生成テスト
```bash
# テストスクリプトを実行
uv run python test_pdf_generation.py
```

このテストでは以下の3つのテンプレートでPDFが生成されます：
1. タイトルページ（title/title-page）
2. 引用文見開きページ（spread/quote-spread）
3. 画像+テキスト片面ページ（single/image-text-single）

### API エンドポイント（実装済み）

#### PDF生成
```bash
POST /generate
```

#### テンプレート一覧取得
```bash
GET /templates
```

#### ヘルスチェック
```bash
GET /health
```

### 使用例（サーバー起動後に利用可能）

#### タイトルページ生成

```bash
curl -X POST http://localhost:8001/generate \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "title/title-page",
    "payload": {
      "title": "旅の思い出",
      "author": "山田太郎",
      "subtitle": "美しい風景との出会い",
      "images": ["1_1080x1920.jpg"],
      "paragraphs": []
    }
  }' --output title_page.pdf
```

#### 引用文見開きページ生成

```bash
curl -X POST http://localhost:8001/generate \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "spread/quote-spread",
    "payload": {
      "title": "人生の名言",
      "author": "名言集",
      "quote": "人生は美しい。それは美しい心で見るからだ。",
      "quote_author": "アンリ・マティス",
      "images": ["2_1080x1920.jpg"],
      "paragraphs": []
    }
  }' --output quote_spread.pdf
```

#### 画像+テキスト片面ページ生成

```bash
curl -X POST http://localhost:8001/generate \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "single/image-text-single",
    "payload": {
      "title": "美しい風景",
      "author": "写真家 田中花子",
      "images": ["3_1080x1920.jpg"],
      "paragraphs": [
        "この風景を見た瞬間、心が洗われるような感覚を覚えました。",
        "自然の美しさは、私たちに多くのことを教えてくれます。"
      ]
    }
  }' --output image_text_single.pdf
```

#### テキスト周り込み画像片面ページ生成

```bash
curl -X POST http://localhost:8001/generate \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "single/text-wrap-image-single",
    "payload": {
      "title": "自然との対話",
      "author": "自然作家 佐藤美咲",
      "images": ["4_1920x1080.jpg", "5_1920x1080.jpg"],
      "paragraphs": [
        "森の中を歩いていると、木々のざわめきが心に響いてきます。風が葉を揺らす音、小鳥のさえずり、そして遠くから聞こえる川のせせらぎ。これらの自然の音は、私たちに何かを語りかけているようです。現代社会では、人工的な音に囲まれて生活することが多いですが、時には自然の中に身を置いて、心をリセットすることも大切です。自然は私たちの心の奥深くにある何かを呼び覚ましてくれます。さらに、季節ごとに変化する森の表情や、朝露に濡れた葉のきらめき、夕暮れ時の静けさなど、自然の中には日常では味わえない特別な瞬間がたくさんあります。私たちは忙しい毎日の中で、つい自然の存在を忘れがちですが、ふと立ち止まって耳を澄ませば、そこには豊かな命の営みが広がっています。自然と向き合うことで、自分自身の心とも静かに対話できるのです。"
      ]
    }
  }' --output text_wrap_image_single.pdf
```

## テスト

### 自動テスト実行

```bash
# 全ページ生成
uv run python test_pdf_generation.py

# 特定のページのみ生成
uv run python test_pdf_generation.py --pages 1 3 4

# 利用可能な画像一覧を表示
uv run python test_pdf_generation.py --images

# 利用可能なテンプレート一覧を表示
uv run python test_pdf_generation.py --templates

# curlコマンド例を表示
uv run python test_pdf_generation.py --curl

# ヘルプを表示
uv run python test_pdf_generation.py --help
```

### ページ番号一覧
1. タイトルページ (title/title-page)
2. 引用文見開きページ (spread/quote-spread)
3. 画像+テキスト片面ページ (single/image-text-single)
4. テキスト周り込み画像片面ページ (single/text-wrap-image-single)

### 利用可能な画像
- **縦長（ポートレート）**: 1_1080x1920.jpg, 2_1080x1920.jpg, 3_1080x1920.jpg, 8_1080x1920.jpg
- **横長（ランドスケープ）**: 4_1920x1080.jpg, 5_1920x1080.jpg
- **正方形**: 6_1080x1080.jpg, 7_1080x1080.jpg, 9_512x512.png

## 利用可能なテンプレート

### 実装済みテンプレート
- `title/title-page` - 背景画像付きタイトルページ
- `spread/quote-spread` - 引用文見開きページ
- `single/image-text-single` - 画像+テキスト片面ページ
- `single/text-wrap-image-single` - テキスト周り込み画像片面ページ（画像が中央に配置され、上下にテキストが周りこむレイアウト）

### 未実装テンプレート
- `spread/text-image-spread` - テキスト+画像見開きページ
- `spread/balanced-spread` - バランス型見開きページ
- `spread/dual-image-spread` - 複数画像見開きページ
- `spread/multi-image-spread` - 多数画像見開きページ
- `spread/academic-spread` - 学術的見開きページ
- `single/text-only-single` - テキストのみ片面ページ
- `single/minimal-single` - ミニマル片面ページ
- `single/text-image-text-single` - テキスト+画像+テキスト片面ページ
- `single/text-focused-single` - テキスト重視片面ページ
- `single/summary-single` - まとめ片面ページ

## サンプル画像

`sample/images/` ディレクトリには以下のサンプル画像が含まれています：

- `1_1080x1920.jpg` - 縦長風景写真
- `2_1080x1920.jpg` - 縦長風景写真
- `3_1080x1920.jpg` - 縦長風景写真
- `4_1920x1080.jpg` - 横長風景写真
- `5_1920x1080.jpg` - 横長風景写真
- `6_1080x1080.jpg` - 正方形写真
- `7_1080x1080.jpg` - 正方形写真
- `8_1080x1920.jpg` - 縦長風景写真
- `9_512x512.png` - アイコン画像

## 開発

### 新しいテンプレートの追加

1. `sample/templates/` に新しいディレクトリを作成
2. `template.html` と `style.css` を作成
3. `app/settings.py` の `ALLOWED_TEMPLATE_IDS` に追加

### ログ確認

```bash
# ログレベルを設定
export LOG_LEVEL=DEBUG
uv run uvicorn app.main:app --reload
```

## トラブルシューティング

### Vivliostyle CLIが見つからない

```bash
# Node.jsとnpmがインストールされているか確認
node --version
npm --version

# Vivliostyle CLIを再インストール
npm uninstall -g vivliostyle-cli
npm install -g vivliostyle-cli

# パスを確認
which vivliostyle
```

### 画像ファイルが見つからない

- 画像ファイルが `sample/images/` に存在するか確認
- ファイル名とパスが正確か確認

### PDF生成エラー

- Vivliostyle CLIのバージョンを確認
- テンプレートファイルの構文を確認
- ログを確認して詳細なエラーメッセージを確認

### Webサーバー起動エラー

- ポート8000が使用中の場合は8001を使用
- 他のプロセスが同じポートを使用していないか確認
- ログを確認して詳細なエラーメッセージを確認

## 次のステップ

1. **Webサーバー起動の安定化**
   - ポート競合の解決
   - エラーハンドリングの改善

2. **APIエンドポイントの動作確認**
   - 各エンドポイントのテスト
   - レスポンス形式の確認

3. **残りテンプレートの実装**
   - 見開きページテンプレート
   - 片面ページテンプレート

4. **機能拡張**
   - 非同期処理・キュー化
   - プレビューAPI（低解像度PNG）
   - テンプレート管理UI
   - ストレージ連携（S3等）

## ライセンス

MIT License
