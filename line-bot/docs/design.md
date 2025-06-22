# LINE Bot 設計ドキュメント

## アーキテクチャ概要

このプロジェクトは、LINE Messaging API v3を使用してLINE Botを実装し、OpenAI APIと統合してChatGPTの機能を提供します。ユーザーのメッセージに対してChatGPTが短文で回答するシンプルなボットです。

**新機能（v2.0）**：ファイル送信・管理機能を追加し、テキスト・音声・動画・ファイルメッセージの受信・送信とAI生成ファイル（レポート・JSON・テキスト）の作成に対応しました。

### 実装詳細

- **モデル**: `gpt-4o-mini`を使用（コスト効率重視）
- **最大トークン数**: 100トークン（短文回答のため）、ファイル生成時は800-1000トークン
- **温度設定**: 0.7（適度な創造性）
- **システムプロンプト**: 「日本語で簡潔に1〜2文で回答してください。長文は避けてください。」
- **ファイル生成**: GPTによるレポート・JSON・テキスト生成機能
- **ファイル管理**: ローカルファイルストレージと静的ファイル配信
- **ファイル受信**: LINE Platform APIを使用したファイルダウンロード
- **ファイル送信制限**: LINE Bot SDK v3では`FileMessage`が利用できないため、ファイル配信はURL付きテキストメッセージで代替

## ファイル構成

```
line-bot/
├── main.py                 # エントリーポイント、FastAPIアプリケーション
├── handlers.py             # Webhook受信処理・HTTPリクエストハンドラー
├── line_service.py         # LINE Bot関連処理（ファイルメッセージ対応）
├── openai_service.py       # OpenAI API関連処理（ファイル生成機能付き）
├── file_service.py         # ファイル管理・メタデータ処理サービス
├── uploads/                # アップロードファイル保存ディレクトリ
├── docs/
│   └── design.md           # 設計ドキュメント（このファイル）
├── README.md               # プロジェクト概要とセットアップ
├── pyproject.toml          # プロジェクト依存関係
└── uv.lock                 # 依存関係ロックファイル
```

## ファイル処理フロー

```
LINE App → ファイル送信 → LINE Platform
                             ↓
LINE Platform → Webhook（ファイルID）→ FastAPI
                             ↓
LINE Service → MessagingApiBlob → ファイルダウンロード
                             ↓
File Service → ファイル保存 → レスポンス生成
                             ↓
LINE Service → テキスト返信 → LINE Platform → LINE App
```

## アーキテクチャフロー

```
LINE Platform → Webhook → FastAPI → LINE Service → OpenAI Service
                              ↓             ↓
                         Response ←────────────────────┘
                              ↓
                         File Service ← Generated Files / Received Files  
                              ↓
                         Static Files → LINE Platform
```

1. **Webhookリクエスト受信**: LINE PlatformからのWebhookを`/callback`エンドポイントで受信
2. **メッセージ解析**: LINE Bot SDK v3を使用してメッセージイベントを解析
3. **ファイル処理**: 
   - ファイルメッセージの場合：LINE Platform APIからファイルをダウンロード・保存
   - テキストメッセージの場合：ファイル生成判定またはChatGPT処理
4. **ChatGPT API呼び出し**: `get_chatgpt_response()`関数でOpenAI APIにメッセージを送信
5. **ファイル生成・保存**: 必要に応じてGPTでファイルを生成し、`file_service`で保存
6. **レスポンス処理**: テキストまたはファイルメッセージをLINE Messaging APIで返信

## 主要コンポーネント

### `main.py`
- **責任**: アプリケーションのエントリーポイント・ファイル配信API
- **機能**: 
  - FastAPIアプリケーションインスタンス
  - `/callback`エンドポイント（LINE Webhook）
  - `/files/{file_id}`（ファイル配信）
  - `/api/files`（ファイル一覧API - デバッグ用）
  - サーバー起動処理

### `handlers.py`
- **責任**: HTTPリクエストハンドラー・Webhook受信処理
- **機能**:
  - LINE Webhookリクエストの受信
  - 署名検証とエラーハンドリング
  - 環境変数の確認とログ出力
  - `handle_webhook()`: メインの処理関数

### `line_service.py`
- **責任**: LINE Bot関連の処理・メッセージタイプ別処理
- **機能**:
  - LINE Bot API設定（`configuration`, `handler`）
  - Webhookファイル受信処理（`handle_image_message()`, `handle_video_message()`, etc.）
  - LINE Platform APIからのファイルダウンロード（`download_file_from_line()`）
  - ファイルメッセージ送信（`send_file_message()`）
  - 動画・音声・ファイルメッセージ作成（`create_message_by_type()`）
  - コマンド処理（ファイル一覧など）
  - ChatGPT連携

### `openai_service.py`
- **責任**: OpenAI API関連の処理・ファイル生成機能
- **機能**:
  - OpenAI クライアント設定
  - ChatGPT API呼び出し（`get_chatgpt_response()`）
  - ファイル生成リクエスト判定（`is_file_generation_request()`）
  - レポート生成
  - JSON生成
  - テキストファイル生成
  - エラーハンドリングと短文レスポンス制御

### `file_service.py`
- **責任**: ファイル管理・メタデータ処理
- **機能**:
  - ファイル保存（`save_file()`）
  - ファイルタイプ判定（`get_message_type()`）
  - ファイルURL生成（`get_file_url()`）
  - ファイル検索・一覧（`get_file_by_id()`, `list_files()`）
  - サポートファイルタイプ管理

## データフロー

### テキストメッセージの場合
1. **ユーザーメッセージ**: LINE app → LINE Platform
2. **Webhook送信**: LINE Platform → `main.py:/callback`
3. **リクエスト処理**: `handlers.py:handle_webhook()`
4. **テキストイベント解析**: `line_service.py:handle_text_message()`
5. **コマンド判定**: 特定コマンド or ChatGPT処理
6. **AI処理**: `openai_service.py:get_chatgpt_response()`
7. **ファイル生成**: 必要に応じてGPTでファイル生成
8. **ファイル保存**: `file_service.py:save_file()`
9. **レスポンス送信**: `line_service.py` → LINE Platform → LINE app

### ファイルメッセージの場合
1. **ユーザーファイル送信**: LINE app → LINE Platform
2. **Webhook送信**: LINE Platform → `main.py:/callback`（ファイルIDを含む）
3. **リクエスト処理**: `handlers.py:handle_webhook()`
4. **ファイルイベント解析**: `line_service.py:handle_[file_type]_message()`
5. **ファイルダウンロード**: `download_file_from_line()` → LINE Platform API
6. **ファイル保存**: `file_service.py:save_file()`
7. **レスポンス送信**: ファイル受信確認 → LINE Platform → LINE app

## サポートするメッセージタイプ

| Webhookイベント | 対応ファイル形式 | LINE Messaging API | 処理関数 |
|------------------|-------------------|---------------------|----------|
| TextMessageContent | テキスト | TextMessage | handle_text_message() |
| ImageMessageContent | JPEG, PNG, GIF | ImageMessage | handle_image_message() |
| VideoMessageContent | MP4, QuickTime | VideoMessage | handle_video_message() |
| AudioMessageContent | MP3, WAV, AAC, M4A | AudioMessage | handle_audio_message() |
| FileMessageContent | PDF, ZIP, TXT, JSON | TextMessage（URL付き） | handle_file_message() |

**注意**: LINE Bot SDK v3では`FileMessage`クラスが利用できないため、ファイル送信時は`TextMessage`でファイル名+ダウンロードURLを提供する形式に変更

## ファイル生成機能

### サポートするコマンド

| コマンド | 機能 | 生成ファイル |
|----------|------|--------------|
| `レポート作成: [テーマ]` | 詳細レポート生成 | テキストファイル |
| `JSON生成: [データ内容]` | JSONデータ生成 | JSONファイル |
| `テキスト生成: [内容]` | テキストファイル生成 | テキストファイル |
| `ファイル一覧` | 保存ファイル一覧表示 | - |
| `サンプル確認` | サンプルPDFファイルを送信 | PDFファイル |

### 使用例

```
ユーザー: レポート作成: 2024年度業績分析
ボット: レポートを生成しました！
       ファイルURL: https://your-domain.com/files/abc123...

ユーザー: [ファイルをLINEで送信]
ボット: ファイルを受信しました！
       ファイル名: document.pdf
       ファイルサイズ: 123456 bytes

ユーザー: サンプル確認
ボット: サンプルPDFファイルを送信します！
       ファイル名: granfa_v8.pdf
       ファイルサイズ: 123456 bytes
       ファイルURL: https://your-domain.com/files/abc123...
```

## API エンドポイント

| エンドポイント | メソッド | 機能 |
|----------------|----------|------|
| `/callback` | POST | LINE Webhook受信 |
| `/files/{file_id}` | GET | ファイル配信 |
| `/api/files` | GET | ファイル一覧取得（デバッグ用） |
| `/api/files/{file_id}` | GET | ファイル情報取得（デバッグ用） |
| `/` | GET | APIドキュメント |

## 環境変数

| 変数名 | 説明 | 取得場所 |
|--------|------|----------|
| `CHANNEL_ACCESS_TOKEN` | LINE Bot Channel Access Token | LINE Developers Console |
| `CHANNEL_SECRET` | LINE Bot Channel Secret | LINE Developers Console |
| `OPENAI_API_KEY` | OpenAI API Key | OpenAI Platform |
| `BASE_URL` | **重要**: 公開ベースURL | サーバー設定 |

## 開発履歴

### LINE Bot SDK v3互換性修正（2025年1月）

1. **FileMessageクラス削除**: LINE Bot SDK v3では`FileMessage`クラスが存在しない問題を修正
   - `line_service.py`から`FileMessage`インポートを削除
   - ファイル送信時は`TextMessage`でファイル名+ダウンロードURLを提供する形式に変更
   - 設計ドキュメントでファイル送信制限を明記

### 画像生成機能削除（2025年1月）

1. **画像生成機能削除**: 不要な画像生成機能を削除
   - `openai_service.py`からDALL-E 3関連のコードを削除
   - `line_service.py`から画像送信デモ機能を削除
   - 設計ドキュメントを更新

### Webhookファイル受信機能追加実装（2025年1月）

1. **Webhookファイル処理追加**: `line_service.py`を更新
   - ImageMessageContent, VideoMessageContent, AudioMessageContent, FileMessageContent対応
   - LINE Platform APIからのファイルダウンロード機能
   - ファイルタイプ別の処理関数

2. **不要なエンドポイント削除**: `main.py`を整理
   - `/upload`エンドポイントを削除（LINE Webhookでファイル受信のため不要）
   - デバッグ用APIのみ保持

### ファイル送信機能追加実装（2025年1月）

1. **ファイル管理サービス追加**: `file_service.py`を新規作成
   - ファイル保存・メタデータ管理
   - ファイルタイプ判定
   - URL生成機能

2. **LINE Bot機能拡張**: `line_service.py`を更新
   - VideoMessage, AudioMessage, FileMessage対応
   - ファイルメッセージ送信機能
   - コマンド処理機能

3. **OpenAI機能拡張**: `openai_service.py`を更新
   - GPTによるレポート・JSON・テキスト生成
   - ファイル生成リクエスト判定

4. **FastAPI拡張**: `main.py`を更新
   - 静的ファイル配信
   - ファイル管理API群

### リファクタリング実装（2025年1月）

1. **コードの分離**: 単一ファイルから機能別に3つのファイルに分離
   - `handlers.py`: HTTPリクエストハンドラー・Webhook受信処理
   - `line_service.py`: LINE Bot関連処理  
   - `openai_service.py`: OpenAI API関連処理
   - `main.py`: エントリーポイント（最小限に）

2. **責任の分離**: 各ファイルが明確な責任を持つように設計
   - Webhook処理とビジネスロジックを分離
   - LINE APIとOpenAI APIの処理を独立化
   - 環境変数の管理を各サービスで適切に実施

3. **保守性の向上**: 
   - モジュール間の結合度を低く維持
   - 各機能の独立性を高めてテスト・デバッグを容易に
   - エントリーポイントを明確化
   - 設計ドキュメントを別ファイルに分離

## 動作確認

### 基本機能
リファクタリング後も、ユーザーからのメッセージがChatGPTに送信され、AIが生成した短文レスポンスがLINEで返信される機能は変わりません。

### ファイル送信機能
- `レポート作成: [内容]` → GPTでレポート生成・ファイル送信
- `JSON生成: [データ]` → GPTでJSON生成・ファイル送信
- `テキスト生成: [内容]` → GPTでテキスト生成・ファイル送信
- `ファイル一覧` → 保存ファイル一覧表示

### ファイル受信機能
- LINE appで動画・音声・ファイルを送信 → 自動でファイル受信・保存・確認メッセージ返信
- `/files/{file_id}` でのファイル配信
- `/api/files` での管理API

## 今後の拡張可能性

- **メタデータ管理**: ファイルタグ・カテゴリ・検索機能
- **コンテキスト保持**: ユーザーごとの会話履歴管理
- **管理機能**: 使用統計、ログ管理機能の追加
- **テスト**: 単体テスト・統合テストの実装
- **データベース**: ファイルメタデータのデータベース管理
- **認証機能**: ファイルアクセス制限・権限管理
- **ファイル処理**: 受信ファイルの音声認識・OCRなどのAI処理 