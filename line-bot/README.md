# LINE Bot with File Support

シンプルなLINE BotとOpenAI ChatGPTの統合プロジェクトです。ユーザーのメッセージに対してChatGPTが日本語で簡潔に回答し、さらにファイル受信・送信・AI生成機能も提供します。

## 主な機能

### 基本機能
- **メッセージ転送**: ユーザーのメッセージをChatGPTに送信
- **短文AI回答**: ChatGPTからの簡潔な回答（1〜2文）をLINEで返信
- **エラーハンドリング**: API呼び出しエラー時の適切な処理

### ファイル受信機能（v2.0）
- **画像受信**: JPEG、PNG、GIF画像をWebhookで受信・保存
- **動画受信**: MP4、QuickTime動画をWebhookで受信・保存
- **音声受信**: MP3、WAV、AAC音声をWebhookで受信・保存
- **ファイル受信**: PDF、ZIP、テキストファイルをWebhookで受信・保存

### ファイル送信機能（v2.0）
- **画像メッセージ**: JPEG、PNG、GIF画像の送信
- **動画メッセージ**: MP4、QuickTime動画の送信
- **音声メッセージ**: MP3、WAV、AAC音声の送信
- **ファイルメッセージ**: PDF、ZIP、テキストファイルの送信

### AI生成機能
- **画像生成**: DALL-E 3による高品質画像生成
- **レポート生成**: GPTによる詳細レポート作成
- **JSON生成**: 構造化データファイル作成
- **テキスト生成**: カスタムテキストファイル作成

## 使用コマンド

| コマンド | 機能 | 例 |
|----------|------|---|
| `画像生成: [プロンプト]` | AI画像生成 | `画像生成: 夕日に向かって走る犬` |
| `レポート作成: [テーマ]` | レポート生成 | `レポート作成: AIの未来について` |
| `JSON生成: [内容]` | JSON作成 | `JSON生成: ユーザー情報のサンプルデータ` |
| `ファイル一覧` | 保存ファイル表示 | `ファイル一覧` |
| `画像送信` | デモ画像送信 | `画像送信` |

## セットアップ

### 1. プロジェクトのクローン

```bash
# プロジェクトをクローン（適宜パスを調整）
cd line-bot
```

### 2. 環境変数の設定

`.env` ファイルを作成して以下の環境変数を設定：

```env
# LINE Bot設定
CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
CHANNEL_SECRET=your_line_channel_secret

# OpenAI API設定
OPENAI_API_KEY=your_openai_api_key

# サーバー設定（本番環境）
BASE_URL=https://your-domain.com

# 開発環境の場合
# BASE_URL=http://localhost:8000
```

### 3. 依存関係のインストール

```bash
# uvを使用してインストール
uv sync
```

### 4. サーバーの起動

```bash
# 開発サーバーを起動
uv run python main.py
```

サーバーは `http://127.0.0.1:8000` で起動します。

## API エンドポイント

| エンドポイント | メソッド | 機能 |
|----------------|----------|------|
| `/` | GET | API情報表示 |
| `/callback` | POST | LINE Webhook受信 |
| `/files/{file_id}` | GET | ファイル配信 |
| `/api/files` | GET | ファイル一覧取得（デバッグ用） |
| `/api/files/{file_id}` | GET | ファイル情報取得（デバッグ用） |

## 外部アクセスの設定（開発時）

LINE Webhookには外部からアクセス可能なURLが必要です。Cloudflare Tunnelを使用：

```bash
# Cloudflare Tunnelで公開
cloudflared tunnel --url localhost:8000
```

出力されたURL（例：`https://example.trycloudflare.com`）をLINE Developers ConsoleのWebhook URLに設定：

```
https://example.trycloudflare.com/callback
```

**重要**: `BASE_URL`環境変数も同じURLに設定してください：

```env
BASE_URL=https://example.trycloudflare.com
```

## API Keys の取得

- **LINE Bot**: [LINE Developers Console](https://developers.line.biz/)でChannel Access TokenとChannel Secretを取得
- **OpenAI**: [OpenAI Platform](https://platform.openai.com/)でAPI Keyを取得（DALL-E 3へのアクセス権限が必要）

## 使用方法

### 基本的な会話
1. LINE BotをLINEアプリで友達追加
2. メッセージを送信
3. ChatGPTが生成した短文回答が返信される

### ファイル受信機能（新機能）
1. LINE Botにファイルを送信：
   - 画像（JPEG、PNG、GIF）
   - 動画（MP4、QuickTime）
   - 音声（MP3、WAV、AAC）
   - ファイル（PDF、ZIP、TXTなど）
2. Botが自動でファイルを受信・保存
3. ファイル受信確認メッセージが返信される

### ファイル生成機能
1. 特定のコマンドを送信：
   - `画像生成: 美しい夕焼けの風景`
   - `レポート作成: 人工知能の現状と将来展望`
   - `JSON生成: ECサイトの商品データサンプル`
2. AIが生成したファイルがLINEで送信される
3. ファイルをタップしてダウンロード・閲覧

### ファイル管理
- `ファイル一覧` で保存されているファイルを確認
- Web API経由でファイルの管理・アクセスが可能

## サポートするファイル形式

| ファイルタイプ | 対応形式 | LINE表示 | 処理 |
|----------------|-----------|----------|------|
| 画像 | JPEG, PNG, GIF | 画像メッセージ | 受信・送信 |
| 動画 | MP4, QuickTime | 動画メッセージ | 受信・送信 |
| 音声 | MP3, WAV, AAC | 音声メッセージ | 受信・送信 |
| ファイル | PDF, ZIP, TXT, JSON | ファイルメッセージ | 受信・送信 |

## ドキュメント

詳細な設計情報とアーキテクチャについては以下を参照：

- **設計ドキュメント**: [`docs/design.md`](docs/design.md)
  - アーキテクチャ概要
  - ファイル構成と責任分離
  - データフローと主要コンポーネント
  - ファイル受信・送信機能の詳細
  - 開発履歴と今後の拡張可能性

## トラブルシューティング

### よくある問題

1. **環境変数エラー**: `.env`ファイルが正しく設定されているか確認
2. **API Key エラー**: LINE・OpenAIのAPI Keyが有効か確認  
3. **Webhook エラー**: Cloudflare TunnelのURLがLINE Consoleに正しく設定されているか確認
4. **ファイル送信エラー**: `BASE_URL`が正しく設定されているか確認
5. **画像生成エラー**: OpenAI APIでDALL-E 3へのアクセス権限があるか確認
6. **ファイル受信エラー**: LINE Platform APIへのアクセス権限があるか確認

### ログの確認

サーバー起動時に環境変数の確認ログが表示されます：

```
CHANNEL_ACCESS_TOKEN: [最初の5文字]... (truncated for security)
CHANNEL_SECRET: [最初の5文字]... (truncated for security)  
OPENAI_API_KEY: [最初の5文字]... (truncated for security)
```

### ファイル関連のトラブル

- **ファイルが受信されない**: Webhook URLが正しく設定されているか確認
- **ファイルが保存されない**: `uploads/`ディレクトリが作成されているか確認
- **画像が表示されない**: `BASE_URL/files/{file_id}`にブラウザでアクセスできるか確認
- **ファイルサイズエラー**: LINE Messaging APIの制限（画像: 10MB, 動画: 200MB, 音声: 200MB, ファイル: 100MB）を確認

## ファイル処理の仕組み

### 受信（Webhook経由）
1. ユーザーがLINE appでファイルを送信
2. LINE PlatformがWebhookでファイルIDを通知
3. BotがLINE Platform APIでファイルをダウンロード
4. ローカルストレージに保存・確認メッセージ送信

### 送信（AI生成）
1. ユーザーがファイル生成コマンドを送信
2. OpenAI APIでファイル内容を生成
3. ローカルストレージに保存
4. LINE Messaging APIでファイルメッセージ送信

## セキュリティ考慮事項

- ファイルサイズ制限の実装
- ディレクトリトラバーサル対策
- ファイルタイプ検証
- 本番環境では適切なファイルアクセス制限を実装

## 開発

コードの構成とアーキテクチャの詳細は [`docs/design.md`](docs/design.md) を参照してください。

### ディレクトリ構造

```
line-bot/
├── main.py                 # FastAPI アプリケーション
├── handlers.py             # Webhook ハンドラー
├── line_service.py         # LINE Bot サービス（ファイル受信・送信）
├── openai_service.py       # OpenAI API サービス（ファイル生成）
├── file_service.py         # ファイル管理サービス
├── uploads/                # ファイル保存ディレクトリ
├── docs/design.md          # 設計ドキュメント
└── README.md               # このファイル
```
