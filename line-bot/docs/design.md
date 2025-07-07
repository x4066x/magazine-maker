# LINE Bot 設計ドキュメント

## アーキテクチャ概要

このプロジェクトは、LINE Messaging API v3を使用してLINE Botを実装し、OpenAI APIと統合してChatGPTの機能を提供します。ユーザーのメッセージに対してChatGPTが短文で回答するシンプルなボットです。

**新機能（v2.0）**：ファイル送信・管理機能を追加し、テキスト・音声・動画・ファイルメッセージの受信・送信とAI生成ファイル（レポート・JSON・テキスト）の作成に対応しました。

**新機能（v3.0）**：auto-designerのPDF生成APIとの連携機能を追加し、ユーザーとの対話を通じて自分史PDFを生成する機能を実装しました。

### 実装詳細

- **モデル**: `gpt-4o-mini`を使用（コスト効率重視）
- **最大トークン数**: 100トークン（短文回答のため）、ファイル生成時は800-1000トークン
- **温度設定**: 0.7（適度な創造性）
- **システムプロンプト**: 「日本語で簡潔に1〜2文で回答してください。長文は避けてください。」
- **ファイル生成**: GPTによるレポート・JSON・テキスト生成機能
- **ファイル管理**: ローカルファイルストレージと静的ファイル配信
- **ファイル受信**: LINE Platform APIを使用したファイルダウンロード
- **ファイル送信制限**: LINE Bot SDK v3では`FileMessage`が利用できないため、ファイル配信はURL付きテキストメッセージで代替
- **PDF生成連携**: auto-designerのv2 APIを使用した自分史PDF生成機能

## ファイル構成

```
line-bot/
├── main.py                 # エントリーポイント、FastAPIアプリケーション
├── handlers.py             # Webhook受信処理・HTTPリクエストハンドラー
├── line_service.py         # LINE Bot関連処理（ファイルメッセージ対応）
├── openai_service.py       # OpenAI API関連処理（ファイル生成機能付き）
├── file_service.py         # ファイル管理・メタデータ処理サービス
├── memoir_service.py       # 自分史作成・PDF生成連携サービス（新規）
├── uploads/                # アップロードファイル保存ディレクトリ
├── docs/
│   └── design.md           # 設計ドキュメント（このファイル）
├── README.md               # プロジェクト概要とセットアップ
├── pyproject.toml          # プロジェクト依存関係
└── uv.lock                 # 依存関係ロックファイル
```

## 自分史作成フロー

```
ユーザー → LINE Bot → 対話型データ収集 → auto-designer API → PDF生成 → ユーザー
```

### 自分史作成の対話フロー

1. **開始**: ユーザーが「自分史作成」または「memoir」と入力
2. **基本情報収集**: 名前、生年月日、出身地などの基本プロフィール
3. **年表作成**: 重要な出来事を年別に収集
4. **画像収集**: 各出来事に関連する画像のアップロード（オプション）
5. **確認・生成**: 収集したデータの確認とPDF生成
6. **配信**: 生成されたPDFをユーザーに送信

### 対話状態管理

```python
class MemoirSession:
    user_id: str
    state: str  # 'idle', 'collecting_profile', 'collecting_timeline', 'collecting_images', 'confirming', 'generating'
    data: MemoirData
    current_step: int
    created_at: datetime
    updated_at: datetime
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
                              ↓
                         Memoir Service → auto-designer API → PDF Generation
```

1. **Webhookリクエスト受信**: LINE PlatformからのWebhookを`/callback`エンドポイントで受信
2. **メッセージ解析**: LINE Bot SDK v3を使用してメッセージイベントを解析
3. **ファイル処理**: 
   - ファイルメッセージの場合：LINE Platform APIからファイルをダウンロード・保存
   - テキストメッセージの場合：ファイル生成判定またはChatGPT処理
4. **自分史作成処理**: 自分史作成モードの場合、対話型データ収集
5. **ChatGPT API呼び出し**: `get_chatgpt_response()`関数でOpenAI APIにメッセージを送信
6. **ファイル生成・保存**: 必要に応じてGPTでファイルを生成し、`file_service`で保存
7. **PDF生成連携**: 自分史データが完成したらauto-designer APIを呼び出し
8. **レスポンス処理**: テキストまたはファイルメッセージをLINE Messaging APIで返信

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
  - 自分史作成対話処理（新規）

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

### `memoir_service.py`（新規）
- **責任**: 自分史作成・PDF生成連携
- **機能**:
  - ユーザーセッション管理（`MemoirSession`）
  - 対話型データ収集
  - auto-designer API連携（`generate_memoir_pdf()`）
  - データバリデーション
  - エラーハンドリング

## データフロー

### テキストメッセージの場合
1. **ユーザーメッセージ**: LINE app → LINE Platform
2. **Webhook送信**: LINE Platform → `main.py:/callback`
3. **リクエスト処理**: `handlers.py:handle_webhook()`
4. **テキストイベント解析**: `line_service.py:handle_text_message()`
5. **コマンド判定**: 特定コマンド or ChatGPT処理 or 自分史作成処理
6. **AI処理**: `openai_service.py:get_chatgpt_response()`
7. **ファイル生成**: 必要に応じてGPTでファイル生成
8. **ファイル保存**: `file_service.py:save_file()`
9. **レスポンス送信**: `line_service.py` → LINE Platform → LINE app

### 自分史作成の場合
1. **ユーザーメッセージ**: LINE app → LINE Platform
2. **Webhook送信**: LINE Platform → `main.py:/callback`
3. **リクエスト処理**: `handlers.py:handle_webhook()`
4. **テキストイベント解析**: `line_service.py:handle_text_message()`
5. **自分史作成判定**: `memoir_service.py:is_memoir_request()`
6. **セッション管理**: `memoir_service.py:get_or_create_session()`
7. **対話処理**: 状態に応じたデータ収集
8. **PDF生成**: `memoir_service.py:generate_memoir_pdf()` → auto-designer API
9. **ファイル保存**: `file_service.py:save_file()`
10. **レスポンス送信**: `line_service.py` → LINE Platform → LINE app

### ファイルメッセージの場合
1. **ユーザーファイル送信**: LINE app → LINE Platform
2. **Webhook送信**: LINE Platform → `main.py:/callback`（ファイルIDを含む）
3. **リクエスト処理**: `handlers.py:handle_webhook()`
4. **ファイルイベント解析**: `line_service.py:handle_[file_type]_message()`
5. **ファイルダウンロード**: `download_file_from_line()` → LINE Platform API
6. **ファイル保存**: `file_service.py:save_file()`
7. **自分史画像処理**: 自分史作成中の場合、画像を年表に追加
8. **レスポンス送信**: ファイル受信確認 → LINE Platform → LINE app

## サポートするメッセージタイプ

| Webhookイベント | 対応ファイル形式 | LINE Messaging API | 処理関数 |
|------------------|-------------------|---------------------|----------|
| TextMessageContent | テキスト | TextMessage | handle_text_message() |
| ImageMessageContent | JPEG, PNG, GIF | ImageMessage | handle_image_message() |
| VideoMessageContent | MP4, QuickTime | VideoMessage | handle_video_message() |
| AudioMessageContent | MP3, WAV, AAC, M4A | AudioMessage | handle_audio_message() |
| FileMessageContent | PDF, ZIP, TXT, JSON | TextMessage（URL付き） | handle_file_message() |

**注意**: LINE Bot SDK v3では`FileMessage`クラスが利用できないため、ファイル送信時は`TextMessage`でファイル名+ダウンロードURLを提供する形式に変更

## 自分史作成機能

### サポートするコマンド

| コマンド | 機能 | 処理 |
|----------|------|------|
| `自分史作成` | 自分史作成モード開始 | 対話型データ収集開始 |
| `memoir` | 自分史作成モード開始 | 対話型データ収集開始 |
| `キャンセル` | 自分史作成をキャンセル | セッション削除・通常モードに戻る |
| `レポート作成: [テーマ]` | 詳細レポート生成 | テキストファイル |
| `JSON生成: [データ内容]` | JSONデータ生成 | JSONファイル |
| `テキスト生成: [内容]` | テキストファイル生成 | テキストファイル |
| `ファイル一覧` | 保存ファイル一覧表示 | - |
| `サンプル確認` | サンプルPDFファイルを送信 | PDFファイル |

### 自分史作成の対話例

```
ユーザー: 自分史作成
ボット: 自分史の作成を開始します！まずは基本情報を教えてください。
       お名前を教えてください。

        💡 ヘルプが必要な場合は「ヘルプ」と入力してください。

ユーザー: 田中太郎
ボット: 田中太郎さんですね！生年月日を教えてください。
       （例：1985年3月15日）

       💡 ヘルプが必要な場合は「ヘルプ」と入力してください。

ユーザー: 1985年3月15日
ボット: 出身地を教えてください。

       💡 ヘルプが必要な場合は「ヘルプ」と入力してください。

ユーザー: 東京都
ボット: 現在の職業を教えてください。

       💡 ヘルプが必要な場合は「ヘルプ」と入力してください。

ユーザー: ソフトウェアエンジニア
ボット: 趣味があれば教えてください。（複数の場合はカンマ区切りで）

       💡 ヘルプが必要な場合は「ヘルプ」と入力してください。

ユーザー: 読書,旅行,写真撮影
ボット: 自己紹介を一言で教えてください。

       💡 ヘルプが必要な場合は「ヘルプ」と入力してください。

ユーザー: IT業界で20年以上働くエンジニアです。
ボット: 基本情報の収集が完了しました！
       次は人生の重要な出来事を年別に教えてください。
       まず、1985年の出来事を教えてください。

       💡 ヘルプが必要な場合は「ヘルプ」と入力してください。

ユーザー: 誕生
ボット: 1985年：誕生
       この出来事について詳しく教えてください。

       💡 ヘルプが必要な場合は「ヘルプ」と入力してください。

ユーザー: 東京都で生まれました。両親と兄の4人家族で育ちました。
ボット: 1985年：誕生
       説明を追加しました。
       次の出来事を教えてください。（例：1991年：小学校入学）

       💡 ヘルプが必要な場合は「ヘルプ」と入力してください。

ユーザー: 1991年：小学校入学
ボット: 1991年：小学校入学
       この出来事について詳しく教えてください。

       💡 ヘルプが必要な場合は「ヘルプ」と入力してください。

ユーザー: 地元の公立小学校に入学。友達と一緒に楽しく学校生活を送りました。
ボット: 1991年：小学校入学
       説明を追加しました。
       次の出来事を教えてください。（例：1997年：中学校入学）

       💡 ヘルプが必要な場合は「ヘルプ」と入力してください。

ユーザー: 完了
ボット: 収集した情報を確認します：

       名前：田中太郎
       生年月日：1985年3月15日
       出身地：東京都
       職業：ソフトウェアエンジニア
       趣味：読書,旅行,写真撮影

       年表：
       - 1985年：誕生
       - 1991年：小学校入学

       PDFを生成しますか？（はい/いいえ）

ユーザー: はい
ボット: PDFを生成中です...しばらくお待ちください。

       自分史PDFが完成しました！
       ファイル名：memoir_田中太郎_20250101_120000.pdf
       ファイルURL：https://your-domain.com/files/abc123...
```

### セッション管理の特徴

- **状態の継続**: 自分史セッション開始後は、すべてのメッセージが自分史作成処理に回される
- **ヘルプ機能**: 各段階で「ヘルプ」と入力することで現在の状態と操作方法を確認可能
- **キャンセル機能**: いつでも「キャンセル」でセッションを終了し、通常モードに戻る
- **エラーハンドリング**: エラー発生時は自動的にセッションをクリア

### PDF生成機能の技術的改善点（2025年1月更新）

#### 問題と解決策

**問題1: 一時ファイルの早すぎる削除**
- **原因**: auto-designer側でPDF生成後に即座に一時ファイルを削除
- **解決策**: HTMLファイルのみ即座に削除し、PDFファイルは保持

**問題2: ファイルメタデータの不整合**
- **原因**: UUIDベースのファイル名とメタデータの不一致
- **解決策**: JSONファイルによるメタデータの永続化

**問題3: LINE側でのファイルアクセス不可**
- **原因**: ファイル配信エンドポイントの不備
- **解決策**: PDFファイル専用の配信機能追加（inline表示対応）

#### 実装された改善点

1. **auto-designer側の修正**:
   - `pdf-cli.ts`: 一時PDFファイルの保持期間を延長
   - HTMLファイルのみ即座に削除、PDFファイルは保持

2. **LINE Bot側の修正**:
   - `file_service.py`: JSONファイルによるメタデータ永続化
   - `main.py`: PDFファイル専用の配信機能追加
   - Content-Dispositionヘッダーの適切な設定

3. **ファイル管理の改善**:
   - メタデータの永続化による正確なファイル情報管理
   - フォールバック機能による既存ファイルの対応
   - ファイルサイズとContent-Typeの正確な取得

#### 技術的改善効果

- **PDFファイルの可視性**: LINE側でPDFファイルが正しく表示される
- **ファイル管理の安定性**: メタデータの永続化による正確な管理
- **エラーハンドリング**: ファイルが見つからない場合の適切な処理
- **パフォーマンス**: 一時ファイルの適切な管理によるリソース最適化

### 技術的改善点（2025年1月更新）

- **reply_tokenエラーハンドリング**: LINE APIの30秒制限に対応
  - `send_text_message_with_fallback()`で自動的にPush messageに切り替え
  - PDF生成処理を非同期化してreply_tokenの期限切れを回避
  - エラー発生時の適切なフォールバック処理

- **非同期PDF生成**: 長時間処理の最適化
  - threadingを使用した非同期処理
  - ユーザーへの即座の応答とPDF生成の並行実行
  - 生成完了後のPush messageによる通知

- **LINE Bot SDK v3対応**: 最新APIへの完全対応
  - v3専用のインポートに統一
  - 例外処理のv3対応
  - 型安全性の向上

- **PDF生成機能の安定化**: ファイル管理と配信の改善
  - メタデータの永続化による正確なファイル管理
  - PDFファイル専用の配信機能追加
  - 一時ファイルの適切な管理

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
| `AUTO_DESIGNER_URL` | auto-designer APIのベースURL | auto-designer設定 |

## 開発履歴

### 自分史PDF生成成功事例（2025年6月30日）

**成功事例**: ユーザー「あ」さんの自分史PDFが正常に生成されました
- **ファイル名**: `memoir_あ_20250630_222219.pdf`
- **ファイルサイズ**: 89,021 bytes（約89KB）
- **ファイルID**: `e3178eca-9f8a-4d39-9066-bf7a0d057735`
- **生成URL**: `https://states-ny-essence-ea.trycloudflare.com/files/e3178eca-9f8a-4d39-9066-bf7a0d057735`
- **生成時刻**: 2025年6月30日 22:22:19

**技術的成果**:
- auto-designer APIとの連携が正常に動作
- ファイルメタデータの永続化が機能
- PDFファイルの配信が正常に動作
- 非同期PDF生成処理が安定動作
- LINE Bot側でのファイルURL表示が正常

**確認された機能**:
- 対話型データ収集（基本情報・年表）
- 画像アップロード機能
- PDF生成・保存・配信
- メタデータ管理
- ファイルアクセス制御

### 自分史作成機能追加（2025年1月）

1. **自分史作成サービス追加**: `memoir_service.py`を新規作成
   - ユーザーセッション管理
   - 対話型データ収集
   - auto-designer API連携

2. **LINE Bot機能拡張**: `line_service.py`を更新
   - 自分史作成コマンド処理
   - 対話状態管理
   - 画像アップロード処理

3. **auto-designer連携**: PDF生成APIとの連携
   - v2 APIエンドポイント使用
   - JSONデータ形式での通信
   - エラーハンドリング

### LINE Bot SDK v3互換性修正（2025年1月）

1. **FileMessageクラス削除**: LINE Bot SDK v3では`FileMessage`クラスが存在しない問題を修正
   - `line_service.py`から`FileMessage`インポートを削除
   - ファイル送信時は`TextMessage`でファイル名+ダウンロードURLを提供する形式に変更
   - 設計ドキュメントでファイル送信制限を明記

2. **reply_tokenエラーハンドリング改善**: LINE APIの「Invalid reply token」エラーに対応
   - `send_text_message_with_fallback()`関数を追加
   - reply_tokenが期限切れ（30秒）の場合、Push messageに自動切り替え
   - PDF生成処理を非同期化してreply_tokenの期限切れを回避
   - エラーハンドリングの強化とログ出力の改善

3. **インポートエラー修正**: LINE Bot SDK v3とv2の混在によるインポートエラーを解決
   - v3専用のインポートに統一
   - 不要なv2インポートを削除
   - 例外処理をv3対応に修正

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

### 自分史作成機能
- `自分史作成` → 対話型データ収集開始
- 基本情報・年表・画像の収集
- auto-designer API連携によるPDF生成
- 生成されたPDFの配信

## 今後の拡張可能性

- **メタデータ管理**: ファイルタグ・カテゴリ・検索機能
- **コンテキスト保持**: ユーザーごとの会話履歴管理
- **管理機能**: 使用統計、ログ管理機能の追加
- **テスト**: 単体テスト・統合テストの実装
- **データベース**: ファイルメタデータのデータベース管理
- **認証機能**: ファイルアクセス制限・権限管理
- **ファイル処理**: 受信ファイルの音声認識・OCRなどのAI処理
- **自分史テンプレート**: 複数のテンプレート選択機能
- **編集機能**: 生成後の自分史PDFの編集・更新機能 