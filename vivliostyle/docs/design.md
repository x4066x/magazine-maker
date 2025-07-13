# 雑誌風 PDF 自動生成サービス（MVP）設計書

## 概要
FastAPI + Python で実装し、Vivliostyle CLI を同期実行して雑誌風PDFを生成するサービス

## システム構成
```
LINE Bot / Web クライアント
    ↓ POST /generate
FastAPI App (Python)
    ↓ application/pdf
クライアント側で閲覧・印刷
```

## 技術スタック
- **Web フレームワーク**: FastAPI 0.116.x
- **テンプレート**: Jinja2
- **PDF 生成**: Vivliostyle CLI 4.x
- **ランタイム**: Python 3.9 + uvicorn
- **パッケージ管理**: uv

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
│   │   ├── 1_1080x1920.jpg
│   │   ├── 2_1080x1920.jpg
│   │   ├── 3_1080x1920.jpg
│   │   ├── 4_1920x1080.jpg
│   │   ├── 5_1920x1080.jpg
│   │   ├── 6_1080x1080.jpg
│   │   ├── 7_1080x1080.jpg
│   │   ├── 8_1080x1920.jpg
│   │   ├── 9_512x512.png
│   │   └── README.md
│   └── templates/         # HTML/CSSテンプレート
│       ├── title/         # タイトルページ
│       │   └── title-page/
│       │       ├── template.html
│       │       └── style.css
│       ├── spread/        # 見開きページ
│       │   └── quote-spread/
│       │       ├── template.html
│       │       └── style.css
│       └── single/        # 片面ページ
│           └── image-text-single/
│               ├── template.html
│               └── style.css
├── docs/                  # 設計ドキュメント
├── requirements.txt       # Python依存関係
├── test_pdf_generation.py # テストスクリプト
└── README.md             # プロジェクト説明
```

## 処理フロー
1. **リクエスト受信**: JSONデータとテンプレートIDを受け取り
2. **テンプレート選択**: `sample/templates/{template_id}/` からHTML/CSSを読み込み
3. **Jinja2 で埋め込み**: 変数置換・ループ処理でHTMLを確定
4. **一時ディレクトリ作成**: `tempfile.TemporaryDirectory()` で作業領域確保
5. **画像ファイル処理**: サンプル画像を一時ディレクトリにコピー
6. **Vivliostyle CLI 実行**: PDF生成
7. **PDF 返却**: `StreamingResponse` でストリーミング
8. **自動クリーンアップ**: 一時ファイルを自動削除

## API 仕様

### POST /generate
**リクエスト**
```json
{
  "template_id": "title/title-page",
  "payload": {
    "title": "旅の思い出",
    "author": "山田太郎",
    "subtitle": "美しい風景との出会い",
    "images": ["1_1080x1920.jpg"],
    "paragraphs": ["本文1", "本文2"],
    "quote": "人生は美しい。それは美しい心で見るからだ。",
    "quote_author": "アンリ・マティス"
  }
}
```

**レスポンス**
- 成功: 200 OK, Content-Type: application/pdf
- エラー: 400 Bad Request / 500 Internal Server Error

### GET /templates
**レスポンス**
```json
{
  "templates": [
    "title/title-page",
    "spread/quote-spread",
    "single/image-text-single"
  ]
}
```

### GET /health
**レスポンス**
```json
{
  "status": "healthy",
  "vivliostyle_cli": "available",
  "vivliostyle_version": "4.0.0"
}
```

## 実装済みテンプレート

### タイトルページ
- **title/title-page**: 背景画像付きタイトルページ
  - 背景画像を全面に配置
  - タイトルと著者名を重ねて表示
  - グラデーション背景

### 見開きページ
- **spread/quote-spread**: 引用文見開きページ
  - 左ページ：画像 + 引用文 + 著者名
  - 右ページ：空白
  - 引用文を強調したレイアウト

### 片面ページ
- **single/image-text-single**: 画像+テキスト片面ページ
  - 上部：タイトル
  - 中部：画像
  - 下部：本文
  - フッター：著者名とページ番号

- **single/text-wrap-image-single**: テキスト周り込み画像片面ページ
  - 上部：タイトル
  - 上部テキスト：最初の2段落
  - 中央：画像（最大2枚、縦に配置）
  - 下部テキスト：残りの段落
  - フッター：著者名とページ番号
  - 特徴：画像が中央に配置され、上下にテキストが周りこむレイアウト

## テンプレート作成方法

### HTML テンプレート例
```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <style>
        {{ css_content }}
    </style>
</head>
<body>
    <div class="page">
        <h1>{{ title }}</h1>
        <p>{{ paragraphs[0] }}</p>
        {% if images and images[0] %}
        <img src="{{ images[0] }}" alt="画像">
        {% endif %}
    </div>
</body>
</html>
```

### CSS テンプレート例
```css
.page {
    width: 210mm;
    height: 297mm;
    padding: 20mm;
    background: #fff;
}

@media print {
    @page {
        size: A4;
        margin: 1cm;
    }
}
```

## セキュリティ・運用
- テンプレートIDをホワイトリスト管理
- 任意HTMLの持ち込み禁止
- 画像サイズ・拡張子の検証
- Vivliostyle実行時間の制限（30秒）
- ログにはパスのみ記録、ユーザデータは残さない

## ローカル動作確認
```bash
# 依存関係インストール
uv sync

# アプリケーション読み込みテスト
uv run python -c "from app.main import app; print('FastAPI app loaded successfully')"

# PDF生成テスト（全ページ）
uv run python test_pdf_generation.py

# PDF生成テスト（特定ページのみ）
uv run python test_pdf_generation.py --pages 1 3 4

# 利用可能な画像一覧表示
uv run python test_pdf_generation.py --images

# 利用可能なテンプレート一覧表示
uv run python test_pdf_generation.py --templates

# 開発サーバー起動（ポート8000が使用中の場合は8001を使用）
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# ヘルスチェック
curl http://localhost:8001/health

# 手動テスト
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

## テストスクリプト機能

### コマンドライン引数
- `--pages, -p`: 生成するページ番号を指定（例: `--pages 1 3 4`）
- `--images, -i`: 利用可能な画像一覧を表示
- `--templates, -t`: 利用可能なテンプレート一覧を表示
- `--curl, -c`: curlコマンド例を表示
- `--help, -h`: ヘルプメッセージを表示

### ページ番号対応
1. タイトルページ (title/title-page)
2. 引用文見開きページ (spread/quote-spread)
3. 画像+テキスト片面ページ (single/image-text-single)
4. テキスト周り込み画像片面ページ (single/text-wrap-image-single)

### 利用可能な画像
- **縦長（ポートレート）**: 1_1080x1920.jpg, 2_1080x1920.jpg, 3_1080x1920.jpg, 8_1080x1920.jpg
- **横長（ランドスケープ）**: 4_1920x1080.jpg, 5_1920x1080.jpg
- **正方形**: 6_1080x1080.jpg, 7_1080x1080.jpg, 9_512x512.png

## 実装状況

### ✅ 完了項目
- [x] FastAPIアプリケーション基盤
- [x] PDF生成サービス（PDFService）
- [x] Pydanticスキーマ定義
- [x] 設定管理（Settings）
- [x] タイトルページテンプレート
- [x] 引用文見開きページテンプレート
- [x] 画像+テキスト片面ページテンプレート
- [x] テキスト周り込み画像片面ページテンプレート
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

### 📋 今後の拡張ポイント
- [ ] 非同期処理・キュー化
- [ ] プレビューAPI（低解像度PNG）
- [ ] テンプレート管理UI
- [ ] ストレージ連携（S3等）
- [ ] 多言語対応
- [ ] テンプレートプレビュー機能
- [ ] バッチ処理対応