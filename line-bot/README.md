# LINE Bot

## アーキテクチャ概要

このプロジェクトは、LINE Messaging API v3を使用してLINE Botを実装し、OpenAI APIと統合してChatGPTの機能を提供します。ユーザーのメッセージに対してChatGPTが短文で回答するシンプルなボットです。

### 主要な機能

1. **メッセージ転送**: ユーザーのメッセージをそのままChatGPTに送信
2. **短文AIレスポンス**: ChatGPTからの簡潔な回答（1〜2文）をLINEで返信
3. **エラーハンドリング**: API呼び出しエラー時の適切な処理

### 実装詳細

- **モデル**: `gpt-4o-mini`を使用（コスト効率重視）
- **最大トークン数**: 100トークン（短文回答のため）
- **温度設定**: 0.7（適度な創造性）
- **システムプロンプト**: 「日本語で簡潔に1〜2文で回答してください。長文は避けてください。」

## 設計ドキュメント

### ファイル構成

```
line-bot/
├── main.py                 # エントリーポイント、すべての機能を含む
├── README.md               # プロジェクトドキュメント
├── pyproject.toml          # プロジェクト依存関係
└── uv.lock                 # 依存関係ロックファイル
```

### アーキテクチャフロー

1. **Webhookリクエスト受信**: LINE PlatformからのWebhookを`/callback`エンドポイントで受信
2. **メッセージ解析**: LINE Bot SDK v3を使用してメッセージイベントを解析
3. **ChatGPT API呼び出し**: `get_chatgpt_response()`関数でOpenAI APIにメッセージを送信
4. **レスポンス処理**: ChatGPTからの短文回答をLINE Messaging APIで返信

### 主要関数

#### `main.py`
- `webhook()`: Webhookリクエストハンドラー
- `handle_message()`: メッセージイベント処理
- `get_chatgpt_response()`: ChatGPT API呼び出し（短文回答）
- `app`: FastAPIアプリケーションインスタンス

## 環境変数の設定

以下の環境変数を `.env` ファイルに設定してください：

```
# LINE Bot設定
CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
CHANNEL_SECRET=your_line_channel_secret

# OpenAI API設定
OPENAI_API_KEY=your_openai_api_key
```

`env_sample.txt` ファイルを参考にして、適切な値を設定してください。

## 開発時の注意点

- 環境変数 `CHANNEL_ACCESS_TOKEN`、`CHANNEL_SECRET`、`OPENAI_API_KEY` が正しく設定されていることを確認してください。
- OpenAI APIキーはセキュリティ上重要なため、適切に管理してください。
- サーバーを再起動する際は、以下のコマンドを使用してください：
  ```
  uv run python main.py
  ```

## Cloudflare Tunnelの使用

ローカル環境で開発・テストを行う際、LINEのWebhookは外部からアクセス可能なURLを必要とします。Cloudflare Tunnelを使用して、ローカルサーバーを外部からアクセス可能なURLに公開することができます。

### Cloudflare Tunnelのセットアップ手順

1. Cloudflare Tunnelをインストールします（`cloudflared`コマンド）。
2. 以下のコマンドを実行して、ローカルサーバーを公開します：
   ```
   cloudflared tunnel --url localhost:8000
   ```
3. 出力されたURL（例：`https://example.trycloudflare.com`）を確認し、LINE Developers ConsoleのWebhook URLに設定します。設定例：
   ```
   https://example.trycloudflare.com/callback
   ```
4. Webhookの検証を行って、設定が正しいことを確認します。

これで、ローカル環境での開発・テストが可能になります。

## 最新の修正内容（2025年1月）

### シンプル実装への変更

1. **複雑なクラス構造を削除**: ChatGPTServiceクラスを削除してシンプルな関数に変更
2. **短文回答の実装**: システムプロンプトで1〜2文での簡潔な回答を指定
3. **トークン数削減**: max_tokensを100に削減してコスト効率を向上
4. **単一ファイル構成**: main.pyにすべての機能を集約

### 動作確認

修正後、ユーザーからのメッセージがChatGPTに送信され、AIが生成した短文レスポンスがLINEで返信されるようになります。
