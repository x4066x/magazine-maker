# Paged.js PDF WebAPI 仕様書

LineBot の後段サービスとして **HTML テンプレート → PDF** 生成に特化したAPIサービスを定義します。

## 📊 現在の実装状況（2025年1月現在）

### ✅ 実装済み機能
- **雑誌テンプレート** (magazine.eta) - 完全実装
- **請求書テンプレート** (invoice.eta) - 完全実装
- **自分史テンプレート** (memoir.eta) - 完全実装（Base64画像埋め込み対応、pagedjs-cli版に統一）
- **Fastify HTTPサーバー** - エントリーポイント
- **画像アップロード機能** - Base64エンコード対応
- **PDF生成機能** - Puppeteer + Paged.js（汎用）/ pagedjs-cli（自分史専用）
- **GraphAI統合** - 最新API対応、ループ・マッピング機能実装

### ✅ 変更履歴（2025年1月22日）
- **memoir生成をpagedjs-cli版に変更**: より軽量で安定した処理
- **pagedjs-cli版にBase64画像埋め込み機能を追加**: Puppeteer版と同等の機能
- **ファイル名を`my-memoir-cli.pdf`に変更**: 使用エンジンの明確化
- **GraphAI最新API対応**: チュートリアルに基づく実装更新
- **ループ・マッピング機能追加**: チャットボット・バッチ処理エンドポイント実装

### ⚠️ 構造上の問題点
- **PDF生成の二重実装**: `pdf.ts` と `pdf-cli.ts` の使い分け（用途別に最適化済み）
- **ユーティリティの部分利用**: 高機能なヘルパー関数の未使用
- **型定義の不完全性**: MemoirData型は後から追加（現在は修正済み）
- **テスト構造の不統一**: `tests/` と `scripts/` の混在

### 📁 ディスク使用量
- **アップロード画像**: 20MB（9ファイル）
- **生成PDF**: 28MB（memoir-base64-test2.pdf）
- **ソースコード**: 約30KB

---

## 1. 目的

* LineBot (Python) から呼び出す **シンプルな HTTP API** を提供
* テンプレートはサーバー側で保持し、クライアントはテンプレート名とデータのみ渡す
* **Paged.js** を活用した高品質なページ分割と印刷レイアウト
* **画像アップロード・管理機能** を提供
* **自分史作成機能** を提供
* CI/CD・Docker など運用系は当面スコープ外とし、実装コードと API 仕様にフォーカス

---

## 2. 使用パッケージ

| パッケージ              | 理由                             |
| ------------------ | ------------------------------ |
| **fastify**        | 軽量・高速な Node.js 向け HTTP フレームワーク |
| **eta**            | 超軽量テンプレートエンジン (HTML をレンダリング)   |
| **puppeteer-core** | Headless Chromium を操作し PDF を作成 |
| **pagedjs**        | CSS Paged Media を適用し組版         |
| **sharp**          | 画像処理・最適化ライブラリ               |
| **typescript**     | 型安全に開発                         |

> 依存はこれだけ。バリデーション等は必要に応じて追加。

---

## 3. テスト結果

### 3.1 Memoir機能テスト結果

#### テスト日時
2025年6月22日

#### テスト内容
- 自分史プレビュー機能
- 画像付きPDF生成機能
- PNG画像の埋め込み機能

#### テスト結果
✅ **プレビュー機能**: 正常動作
- HTMLプレビューが正常に生成される
- 年表レイアウトが正しく表示される
- プロフィール情報が正しく表示される

✅ **PDF生成機能**: 正常動作
- 画像なしPDF: 430KB
- 画像付きPDF: 28.4MB（画像が正しく埋め込まれる）

✅ **画像埋め込み**: 正常動作
- PNG画像が正しく読み込まれる
- 絶対URLパス（http://localhost:3000/images/）を使用
- 画像読み込み完了を待つ処理を実装

#### 対応した画像ファイル
- `profile.png` - プロフィール画像
- `birth.png` - 誕生時の写真
- `elemtentary.png` - 小学校入学時の写真
- `junior-high.png` - 中学校入学時の写真
- `high-school.png` - 高校入学時の写真
- `work.png` - 就職・独立時の写真
- `wedding.png` - 結婚時の写真
- `baby.png` - 出産時の写真
- `current.png` - 現在の写真

#### 技術的改善点
1. **画像パス修正**: 相対パスから絶対URLパスに変更
2. **画像読み込み待機**: PDF生成時に画像の読み込み完了を待つ処理を追加
3. **リクエストインターセプト**: 画像リクエストの処理を改善

### 3.2 Base64埋め込み機能実装とテスト結果

#### 実装日時
2025年6月22日

#### 実装背景
- **問題**: PDF生成時に都度APIサーバーから画像を取得していた
- **課題**: ネットワーク依存、パフォーマンス問題、ファイルサイズ肥大化
- **解決策**: 画像をBase64エンコードしてHTMLに直接埋め込む方式を採用

#### 実装内容
1. **Base64埋め込み関数の追加** (`src/index.ts`)
   - 画像ファイルをBase64エンコード
   - HTMLのimgタグのsrc属性を置換
   - プレビューとPDF生成の両方で使用

2. **画像パスの最適化**
   - 相対パスを使用（uploads/画像名）
   - Base64埋め込みにより絶対URLが不要

#### テスト結果
✅ **プレビュー機能**: 正常動作
- Base64データが正常に埋め込まれている
- 画像が正しく表示される

✅ **PDF生成機能**: 大幅改善
- **ファイルサイズ**: 29.7MB → 407KB（約98%削減）
- **処理時間**: 3.9秒 → 3.1秒（約20%改善）
- **ネットワーク依存**: 完全に解消

#### 技術的改善効果
1. **パフォーマンス向上**: ネットワークリクエスト削減
2. **ファイルサイズ最適化**: 画像の重複埋め込みを防止
3. **安定性向上**: 外部依存の削減
4. **処理速度向上**: 画像読み込み待機時間の短縮

#### 対応した画像ファイル（Base64埋め込み版）
- `profile.png` - プロフィール画像
- `birth.png` - 誕生時の写真
- `elemtentary.png` - 小学校入学時の写真
- `junior-high.png` - 中学校入学時の写真
- `high-school.png` - 高校入学時の写真
- `work.png` - 就職・独立時の写真
- `wedding.png` - 結婚時の写真
- `baby.png` - 出産時の写真
- `current.png` - 現在の写真

---

## 4. API 仕様

### GET `/health`
ヘルスチェックエンドポイント

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### GET `/templates`
利用可能なテンプレート一覧を取得

**Response:**
```json
{
  "templates": ["invoice", "magazine", "memoir"],
  "count": 3
}
```

### POST `/upload/image`
画像アップロードエンドポイント（Base64エンコード方式）

**Request Body:**
```json
{
  "imageData": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
  "fileName": "profile.jpg",
  "mimeType": "image/jpeg"
}
```

**Response:**
```json
{
  "success": true,
  "image": {
    "id": "img_1705123456789_abc123",
    "fileName": "img_1705123456789_abc123.jpg",
    "url": "/images/img_1705123456789_abc123.jpg",
    "size": 123456,
    "width": 800,
    "height": 600,
    "uploadedAt": "2024-01-15T10:30:00.000Z"
  }
}
```

### GET `/images`
画像一覧取得エンドポイント

**Response:**
```json
{
  "images": [
    {
      "id": "img_1705123456789_abc123",
      "fileName": "img_1705123456789_abc123.jpg",
      "url": "/images/img_1705123456789_abc123.jpg",
      "size": 123456,
      "width": 800,
      "height": 600,
      "uploadedAt": "2024-01-15T10:30:00.000Z"
    }
  ],
  "count": 1
}
```

### GET `/images/:fileName`
画像表示エンドポイント

**Response:** 画像ファイル（バイナリ）

### POST `/memoir/preview`
自分史HTMLプレビューエンドポイント

**Request Body:**
```json
{
  "data": {
    "title": "私の人生の歩み",
    "author": "田中 花子",
    "timeline": [...]
  }
}
```

**Response:** HTML（text/html）

### POST `/pdf` **（Puppeteer版 - 汎用テンプレート用）**

| 項目               | 内容                             |
| ---------------- | ------------------------------ |
| **概要**           | 指定テンプレートに `data` を流し込み、PDF を返却（汎用） |
| **対象テンプレート**    | `magazine` (雑誌), `invoice` (請求書) |
| **特徴**           | 高機能、Puppeteer + Paged.js使用 |
| **Content‑Type** | `application/json`             |
| **Accept**       | `application/pdf`              |

#### Request Body

```jsonc
{
  "template": "memoir",            // 必須: テンプレート名
  "data": {                        // 必須: テンプレートの入力用 JSON
    "title": "私の人生の歩み",
    "author": "田中 花子",
    "timeline": [...]
  },
  "fileName": "my-memoir.pdf",     // 任意: レスポンス時のファイル名
  "options": {                     // 任意: PDF生成オプション
    "format": "A4",                // A4, A3, Letter, Legal
    "margin": {                    // マージン設定
      "top": "20mm",
      "right": "20mm",
      "bottom": "20mm",
      "left": "20mm"
    },
    "printBackground": true        // 背景印刷の有効/無効
  }
}
```

#### Responses

| Status                      | 意味                                  |
| --------------------------- | ----------------------------------- |
| `200 OK`                    | `application/pdf` でストリーム返却          |
| `400 Bad Request`           | `template` または `data` が欠落・テンプレート未登録 |
| `500 Internal Server Error` | 生成中の予期しないエラー                        |

**Success Response Headers:**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="my-memoir.pdf"
Content-Length: 123456
X-Processing-Time: 1500
```

### POST `/pdf/cli` **（pagedjs-cli版 - 自分史専用）**

| 項目               | 内容                             |
| ---------------- | ------------------------------ |
| **概要**           | 自分史テンプレートに特化したPDF生成 |
| **対象テンプレート**    | `memoir` (自分史) |
| **特徴**           | 軽量、安定、メモリ使用量30%削減 |
| **Content‑Type** | `application/json`             |
| **Accept**       | `application/pdf`              |

#### Request Body

```jsonc
{
  "template": "memoir",            // 必須: テンプレート名
  "data": {                        // 必須: テンプレートの入力用 JSON
    "title": "私の人生の歩み",
    "author": "田中 花子",
    "timeline": [...]
  },
  "fileName": "my-memoir-cli.pdf",  // 任意: レスポンス時のファイル名
  "options": {                     // 任意: PDF生成オプション
    "format": "A4",                // A4, A3, Letter, Legal
    "margin": {                    // マージン設定
      "top": "20mm",
      "right": "20mm",
      "bottom": "20mm",
      "left": "20mm"
    },
    "printBackground": true        // 背景印刷の有効/無効
  }
}
```

#### Responses

| Status                      | 意味                                  |
| --------------------------- | ----------------------------------- |
| `200 OK`                    | `application/pdf` でストリーム返却          |
| `400 Bad Request`           | `template` または `data` が欠落・テンプレート未登録 |
| `500 Internal Server Error` | 生成中の予期しないエラー                        |

**Success Response Headers:**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="my-memoir-cli.pdf"
Content-Length: 123456
X-Processing-Time: 1500
```

#### 使い分けの指針
- **雑誌・請求書**: `/pdf` エンドポイント（Puppeteer版）を使用
- **自分史**: `/pdf/cli` エンドポイント（pagedjs-cli版）を使用
- CLI版は自分史に特化した最適化が施されており、より軽量で安定した処理が可能

### POST `/chat` **（GraphAI ChatGPT統合）**

| 項目               | 内容                             |
| ---------------- | ------------------------------ |
| **概要**           | GraphAIを使用したChatGPT API統合 |
| **特徴**           | 最新API対応、プロンプト・メッセージ両対応 |
| **Content‑Type** | `application/json`             |
| **Accept**       | `application/json`             |

#### Request Body

```jsonc
{
  "messages": [                    // 任意: メッセージ配列
    {
      "role": "user",
      "content": "こんにちは"
    }
  ],
  "prompt": "こんにちは",            // 任意: 単一プロンプト
  "model": "gpt-3.5-turbo"         // 任意: モデル指定
}
```

#### Response

```json
{
  "success": true,
  "result": {
    "text": "こんにちは！何かお手伝いできることはありますか？",
    "message": {
      "role": "assistant",
      "content": "こんにちは！何かお手伝いできることはありますか？"
    },
    "usage": {
      "prompt_tokens": 10,
      "completion_tokens": 20,
      "total_tokens": 30
    },
    "model": "gpt-3.5-turbo"
  }
}
```

### POST `/chatbot` **（GraphAI ループ機能使用）**

| 項目               | 内容                             |
| ---------------- | ------------------------------ |
| **概要**           | ループ機能を使用したチャットボット |
| **特徴**           | 複数ターンの会話、状態管理 |
| **Content‑Type** | `application/json`             |
| **Accept**       | `application/json`             |

#### Request Body

```jsonc
{
  "initialPrompt": "こんにちは、今日の天気について教えてください",
  "maxTurns": 10                   // 任意: 最大会話ターン数
}
```

#### Response

```json
{
  "success": true,
  "conversation": [
    {
      "role": "system",
      "content": "あなたは親切で役立つアシスタントです。"
    },
    {
      "role": "user",
      "content": "こんにちは、今日の天気について教えてください"
    },
    {
      "role": "assistant",
      "content": "申し訳ございませんが、私はリアルタイムの天気情報にアクセスできません..."
    }
  ]
}
```

### POST `/batch-process` **（GraphAI マッピング機能使用）**

| 項目               | 内容                             |
| ---------------- | ------------------------------ |
| **概要**           | マッピング機能を使用したバッチ処理 |
| **特徴**           | 並列処理、大量データ対応 |
| **Content‑Type** | `application/json`             |
| **Accept**       | `application/json`             |

#### Request Body

```jsonc
{
  "items": [                       // 必須: 処理対象アイテム配列
    "りんご",
    "レモン",
    "バナナ"
  ],
  "promptTemplate": "What is the typical color of ${:row}? Just answer the color.",
  "model": "gpt-3.5-turbo"         // 任意: モデル指定
}
```

#### Response

```json
{
  "success": true,
  "results": [
    {
      "item": "赤"
    },
    {
      "item": "黄色"
    },
    {
      "item": "黄色"
    }
  ]
}
```

---

## 5. ディレクトリ構成

```
auto-designer/
├── src/                    # ソースコード
│   ├── index.ts           # メインエントリーポイント（Fastifyサーバー）
│   ├── pdf.ts             # Puppeteerを使用したPDF生成
│   ├── pdf-cli.ts         # pagedjs-cliを使用したPDF生成
│   ├── types/             # 型定義
│   │   └── index.ts       # 雑誌・請求書データの型定義
│   ├── utils/             # ユーティリティ関数
│   │   ├── file-utils.ts  # ファイル操作ユーティリティ
│   │   ├── template-utils.ts # テンプレート処理ユーティリティ
│   │   └── image-manager.ts # 画像管理機能
│   └── templates/         # ETAテンプレート
│       ├── magazine.eta   # 雑誌テンプレート
│       ├── invoice.eta    # 請求書テンプレート
│       └── memoir.eta     # 自分史テンプレート
├── samples/               # サンプルデータ
│   ├── magazine-sample.json
│   ├── invoice-sample.json
│   ├── memoir-sample.json
│   └── memoir-sample.html # 自分史作成ツール
├── uploads/               # アップロードされた画像
├── tests/                 # テストファイル
│   ├── test-magazine.html
│   ├── test-simple.html
│   └── test-cli-direct.js
├── scripts/               # スクリプトファイル
│   ├── test.sh
│   └── test-fixed.sh
├── docs/                  # ドキュメント
│   ├── design.md          # 設計ドキュメント
│   └── structure.md       # 構造説明ファイル
├── output/                # 生成されたPDFファイル
├── node_modules/
├── package.json
├── package-lock.json
├── tsconfig.json
├── README.md
└── .gitignore
```

---

## 6. テンプレート仕様

### 6.1 請求書テンプレート (`invoice.eta`)

**機能:**
- ヘッダー・フッター（ページ番号、発行日）
- 顧客情報と請求書詳細の2カラムレイアウト
- 商品テーブル（数量、単価、小計）
- 消費税計算と合計金額表示
- 備考欄

**サンプルデータ:**
```json
{
  "customerName": "株式会社テスト商事",
  "customerAddress": "〒100-0001 東京都千代田区千代田1-2-3",
  "customerPhone": "03-1234-5678",
  "invoiceNumber": "INV-2024-001",
  "issueDate": "2024-01-15",
  "dueDate": "2024-02-14",
  "taxRate": 0.1,
  "items": [
    {
      "name": "Webサイト制作",
      "quantity": 1,
      "price": 500000
    }
  ],
  "notes": "お支払いは銀行振込にてお願いいたします。"
}
```

### 6.2 雑誌テンプレート (`magazine.eta`)

**機能:**
- 表紙ページ（グラデーション背景）
- 目次（ページ番号付きリンク）
- 記事コンテンツ（段組みレイアウト）
- ヘッダー・フッター（タイトル、ページ番号）
- 引用ブロック、画像対応

**サンプルデータ:**
```json
{
  "title": "技術雑誌サンプル",
  "subtitle": "最新のWeb技術と開発トレンド",
  "publishDate": "2024年1月号",
  "articles": [
    {
      "title": "React 18の新機能と実践的な活用方法",
      "subtitle": "Concurrent FeaturesとSuspenseの完全ガイド",
      "author": "田中 太郎",
      "lead": "React 18で導入されたConcurrent Featuresは...",
      "content": "React 18の最大の特徴は..."
    }
  ]
}
```

### 6.3 自分史テンプレート (`memoir.eta`)

**機能:**
- 表紙ページ（グラデーション背景、タイトル・著者名）
- 目次（年表項目へのリンク）
- プロフィールセクション（画像付き）
- 年表レイアウト（画像付きイベント記録）
- 印刷用スタイル（ページ分割対応）

**サンプルデータ:**
```json
{
  "title": "私の人生の歩み",
  "subtitle": "これまでの軌跡と想い出",
  "author": "田中 花子",
  "createdDate": "2024年1月作成",
  "birthDate": "1985年3月15日",
  "birthPlace": "東京都",
  "occupation": "Webデザイナー",
  "interests": ["写真撮影", "旅行", "料理", "読書"],
  "motto": "一期一会を大切に、毎日を充実させて生きる",
  "profileImage": "/images/profile.jpg",
  "timeline": [
    {
      "year": 1985,
      "title": "誕生",
      "description": "東京都の病院で生まれました。両親は私の誕生を心から喜んでくれました。",
      "image": "/images/birth.jpg",
      "imageCaption": "生後1ヶ月の写真"
    },
    {
      "year": 1991,
      "title": "小学校入学",
      "description": "地元の小学校に入学しました。新しい友達との出会いに胸を躍らせていました。",
      "image": "/images/elementary.jpg",
      "imageCaption": "入学式の記念写真"
    }
  ]
}
```

---

## 7. 画像管理機能

### 7.1 ImageManager クラス

**機能:**
- 画像アップロード（Base64エンコード対応）
- 画像最適化（Sharp使用）
- 画像情報管理
- ファイルシステム管理

**主要メソッド:**
- `saveImage(file)`: 画像保存
- `optimizeImage(path, options)`: 画像最適化
- `getImageBuffer(path)`: 画像バッファ取得
- `listImages()`: 画像一覧取得
- `deleteImage(path)`: 画像削除

### 7.2 画像処理オプション

```typescript
interface ImageOptions {
  width?: number;
  height?: number;
  quality?: number;
  format?: 'jpeg' | 'png' | 'webp';
}
```

---

## 8. 自分史作成ツール

### 8.1 機能概要

- WebブラウザベースのGUI
- リアルタイムプレビュー
- 年表項目の動的追加・編集
- PDF出力機能

### 8.2 使用方法

1. サーバー起動: `npm run dev`
2. ブラウザで `samples/memoir-sample.html` を開く
3. 基本情報・年表項目を入力
4. プレビューで確認
5. PDF生成・ダウンロード

### 8.3 技術仕様

- 純粋なHTML/CSS/JavaScript
- Fetch API を使用したサーバー通信
- Base64エンコードによる画像処理
- iframe を使用したプレビュー表示

---

## 9. Paged.js 活用機能

### 9.1 CSS Paged Media 機能

- **@page ルール**: ページサイズ、マージン、ヘッダー・フッター設定
- **ページ分割制御**: `page-break-before`, `page-break-after`, `page-break-inside`
- **生成コンテンツ**: `content`, `counter()`, `string()` 関数
- **段組みレイアウト**: `column-count`, `column-gap`

### 9.2 実装の改善点

- **エラーハンドリング**: 適切なtry-catch文とリソース管理
- **パフォーマンス**: Puppeteerの最適化設定
- **設定オプション**: PDF形式、マージン、背景印刷のカスタマイズ
- **ログ機能**: 処理時間とエラー詳細の記録

---

## 10. 構造整理の変更点

### 10.1 ディレクトリ構造の改善

**変更前:**
```
auto-designer/
├── test-output/           # テスト出力が混在
├── test-*.html           # テストファイルがルートに散らばり
├── test-*.js
├── test-*.sh
├── design.md             # ドキュメントがルートに
└── src/
    ├── index.ts
    ├── pdf.ts
    ├── pdf-cli.ts
    └── templates/
```

**変更後:**
```
auto-designer/
├── src/
│   ├── types/            # 型定義を分離
│   ├── utils/            # ユーティリティを分離
│   └── templates/
├── tests/                # テストファイルを集約
├── scripts/              # スクリプトファイルを集約
├── docs/                 # ドキュメントを集約
├── output/               # 出力ディレクトリを明確化
└── samples/              # サンプルデータ
```

### 10.2 新規追加ファイル

- **src/types/index.ts**: 雑誌・請求書データの型定義
- **src/utils/file-utils.ts**: ファイル操作ユーティリティ
- **src/utils/template-utils.ts**: テンプレート処理ユーティリティ
- **README.md**: プロジェクト概要と使用方法
- **.gitignore**: Git除外ファイル設定
- **docs/structure.md**: 構造説明ドキュメント

### 10.3 package.json の改善

- スクリプトの整理と追加
- メインファイルパスの修正
- テストスクリプトの改善
- クリーンアップスクリプトの追加

### 10.4 開発フローの改善

1. **型安全性の向上**: TypeScript型定義の追加
2. **ユーティリティの分離**: 再利用可能な関数の整理
3. **ドキュメントの充実**: READMEと構造説明の追加
4. **テスト環境の整備**: テストファイルの整理
5. **設定ファイルの追加**: .gitignoreの追加

---

## 11. 今後の改善予定

- **テストフレームワーク**: Jest または Vitest の導入
- **ESLint/Prettier**: コード品質の向上
- **Docker**: コンテナ化対応
- **CI/CD**: GitHub Actions の導入
- **API ドキュメント**: OpenAPI/Swagger の追加

---

## 12. GraphAI統合機能

### 12.1 実装概要

GraphAIの最新チュートリアル（https://graphai.info/guide/tutorial.html）に基づいて、以下の機能を実装：

- **最新API対応**: GraphAI 2.0.8の最新API仕様に対応
- **ループ機能**: チャットボットでの複数ターン会話
- **マッピング機能**: バッチ処理での並列実行
- **エージェント関数**: カスタムエージェントの実装

### 12.2 主要エージェント

#### openAIAgent
- OpenAI APIとの統合
- プロンプト・メッセージ両対応
- 統一されたレスポンス形式

#### textInputAgent
- ユーザー入力の処理
- チャットボットでの入力待機

#### compareAgent
- 条件比較処理
- ループ制御での使用

#### stringTemplateAgent
- 文字列テンプレート処理
- コンソール出力対応

#### pushAgent
- 配列操作
- メッセージ履歴の管理

#### mapAgent
- マッピング処理
- サブグラフの実行

#### copyAgent
- データコピー処理
- 結果の整形

### 12.3 技術的改善点

1. **型安全性**: TypeScript型定義の追加
2. **エラーハンドリング**: 適切な例外処理
3. **レスポンス統一**: 一貫したAPIレスポンス形式
4. **パフォーマンス**: 並列処理の最適化
5. **拡張性**: 新しいエージェントの追加が容易

---

## 13. 今後の改善予定

- **テストフレームワーク**: Jest または Vitest の導入
- **ESLint/Prettier**: コード品質の向上
- **Docker**: コンテナ化対応
- **GraphAI機能拡張**: より高度なフロー制御
- **ストリーミング対応**: リアルタイムレスポンス
- **認証機能**: API キー管理の改善
