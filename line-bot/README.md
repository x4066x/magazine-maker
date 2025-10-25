# LINE Bot - 自分史作成サービス

LINE BotとOpenAI ChatGPTを統合した対話型の自分史作成サービスです。ユーザーとの会話を通じて情報を収集し、美しいPDFの自分史を生成します。

## 主な機能

- **簡易フロー**: タイトル + カバー写真だけで即座にPDF生成
- **Web編集画面**: ブラウザで自分史を編集（テキスト、画像、年表）
- **AI文章生成**: プロフィールや年表説明文をAIが自動生成
- **PDF生成**: Vivliostyleを使用した美しいPDF自動生成
- **対話型自分史作成**: ユーザーとの対話で詳細情報を収集
- **画像管理**: 画像のアップロード、ダウンロード、最適化
- **柔軟なカスタマイズ**: 用紙サイズ、トンボ、裁ち落としなど印刷用設定

## クイックスタート

### 1. 環境変数の設定

`.env`ファイルを作成：

```env
# LINE Bot設定
CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
CHANNEL_SECRET=your_line_channel_secret

# OpenAI API設定
OPENAI_API_KEY=your_openai_api_key

# サーバー設定
BASE_URL=https://your-domain.com
AUTO_DESIGNER_URL=http://localhost:3000
```

### 2. インストールと起動

```bash
# 依存関係のインストール
uv sync

# サーバー起動
uv run python main.py
```

### 3. 外部アクセス設定（開発時）

```bash
# Cloudflare Tunnelで公開
cloudflared tunnel --url localhost:8000
```

出力されたURLをLINE Developers ConsoleのWebhook URLに設定してください。

## 使い方

### 簡易フロー（おすすめ）

**最速で自分史を作成！**

```
ユーザー: 作る
ボット: ✨ 自分史を作成しましょう！
       まず、タイトルを教えてください。

ユーザー: 鈴木一郎
ボット: タイトル：「鈴木一郎」
       次に、カバー写真を送ってください。

[写真を送信]
ボット: カバー写真を受け取りました！
       PDFを生成中です...⏳

[数秒後]
ボット: ✨ 自分史完成！
       📄 PDFを見る
       ✏️ 内容を編集
```

### 詳細フロー（従来）

より詳しい情報を最初から入力したい場合：

```
ユーザー: 自分史作成
ボット: 自分史の作成を開始します！まずは基本情報を教えてください。
```

以下の流れで対話が進みます：
1. 基本情報の収集（名前、生年月日、出身地、職業、趣味）
2. 人生の年表作成（年別の重要な出来事）
3. 画像のアップロード（オプション）
4. 確認とPDF生成

### その他のコマンド

| コマンド | 機能 |
|----------|------|
| `作る` / `作成` / `つくる` | 簡易フロー開始（おすすめ） |
| `自分史作成` / `memoir` | 詳細フロー開始 |
| `キャンセル` | 作成をキャンセル |
| `ファイル一覧` | 保存ファイルを表示 |
| `サンプル確認` | サンプルPDFを表示 |
| 通常のメッセージ | ChatGPTと会話 |

## プロジェクト構成

```
line-bot/
├── main.py                            # エントリーポイント
├── app/
│   ├── main.py                       # FastAPI アプリ
│   ├── config/settings.py            # 設定
│   ├── api/routes.py                 # API ルート
│   ├── handlers/webhook_handler.py   # Webhook ハンドラー
│   └── services/
│       ├── line_service.py           # LINE連携
│       ├── quick_memoir_service.py   # 簡易フロー ★NEW
│       ├── vivliostyle_service.py    # PDF生成 ★NEW
│       ├── openai_service.py         # AI文章生成
│       ├── file_service.py           # ファイル管理
│       └── memoir_service.py         # 詳細フロー
├── templates/                         # テンプレート ★NEW
│   └── memoir/
│       └── template.html             # 自分史HTMLテンプレート
├── liff/                              # Web編集画面 ★NEW
│   └── edit.html                     # 編集画面
├── uploads/                           # ファイル保存先
└── docs/                              # ドキュメント ★拡充
    ├── README.md                     # ドキュメント一覧
    ├── design.md                     # 設計
    ├── quick-flow-guide.md           # 簡易フローガイド
    ├── vivliostyle-integration.md    # Vivliostyle統合
    ├── vivliostyle-options.md        # オプション設定
    └── troubleshooting-vivliostyle.md # トラブルシューティング
```

## 📚 ドキュメント

詳細なドキュメントは [`docs/`](./docs/) ディレクトリを参照してください：

### メインドキュメント
- **[docs/README.md](./docs/README.md)** - 📖 ドキュメント一覧・ナビゲーション
- **[docs/design.md](./docs/design.md)** - 🎯 設計・要求定義
- **[docs/quick-flow-guide.md](./docs/quick-flow-guide.md)** - 🚀 簡易フロー実装ガイド

### 技術ドキュメント
- **[docs/vivliostyle-integration.md](./docs/vivliostyle-integration.md)** - 📄 Vivliostyle統合ガイド
- **[docs/vivliostyle-options.md](./docs/vivliostyle-options.md)** - ⚙️ Vivliostyleオプション設定
- **[docs/troubleshooting-vivliostyle.md](./docs/troubleshooting-vivliostyle.md)** - 🔧 トラブルシューティング

### クイックリンク
- 初めての方 → [docs/README.md - 読む順序](./docs/README.md#読む順序推奨)
- トラブル発生時 → [docs/troubleshooting-vivliostyle.md](./docs/troubleshooting-vivliostyle.md)
- PDF設定変更 → [docs/vivliostyle-options.md](./docs/vivliostyle-options.md)

## API Keys の取得

- **LINE Bot**: [LINE Developers Console](https://developers.line.biz/)
- **OpenAI**: [OpenAI Platform](https://platform.openai.com/)
