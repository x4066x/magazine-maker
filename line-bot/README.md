# LINE Bot - 自分史作成サービス

LINE BotとOpenAI ChatGPTを統合した対話型の自分史作成サービスです。ユーザーとの会話を通じて情報を収集し、美しいPDFの自分史を生成します。

## 主な機能

- **対話型自分史作成**: ユーザーとの対話で基本情報と人生の年表を収集
- **画像アップロード**: 年表の各出来事に画像を追加可能
- **PDF生成**: auto-designer APIを使用した自分史PDFの自動生成
- **AI会話**: ChatGPTによる自然な対話応答
- **ファイル管理**: 画像・動画・音声・ファイルの受信・送信

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

### 自分史作成

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
| `自分史作成` / `memoir` | 自分史作成を開始 |
| `キャンセル` | 作成をキャンセル |
| `ファイル一覧` | 保存ファイルを表示 |
| `レポート作成: [テーマ]` | AIレポート生成 |
| `JSON生成: [内容]` | JSON生成 |

## プロジェクト構成

```
line-bot/
├── main.py                     # エントリーポイント
├── app/
│   ├── main.py                # FastAPI アプリ
│   ├── config/settings.py     # 設定
│   ├── api/routes.py          # API ルート
│   ├── handlers/webhook_handler.py
│   └── services/
│       ├── line_service.py
│       ├── openai_service.py
│       ├── file_service.py
│       └── memoir_service.py
├── uploads/                   # ファイル保存先
└── docs/design.md             # 設計ドキュメント
```

## ドキュメント

詳細は [`docs/design.md`](docs/design.md) を参照してください：
- アーキテクチャ設計
- データフローと処理の詳細
- 自分史作成機能の実装
- トラブルシューティング
- セキュリティ考慮事項

## API Keys の取得

- **LINE Bot**: [LINE Developers Console](https://developers.line.biz/)
- **OpenAI**: [OpenAI Platform](https://platform.openai.com/)
