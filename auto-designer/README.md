# Auto Designer

自動的にPDFデザインを生成するツール

## 📊 現在の実装状況（2025年1月22日）

### ✅ 完全実装済み
- **雑誌形式のPDF自動生成** - 高品質な段組みレイアウト（Puppeteer版）
- **請求書形式のPDF自動生成** - ビジネス文書対応（Puppeteer版）
- **自分史形式のPDF自動生成** - 年表レイアウト + 画像対応（**pagedjs-cli版に統一**）
- **画像アップロード機能** - Base64エンコード対応
- **HTTPサーバーAPI** - Fastify による高速API

### ✅ 最新の改善点（2025年1月22日）
- **memoir生成エンジンの最適化**: Puppeteer版からpagedjs-cli版へ変更
- **軽量化の実現**: より安定した処理とメモリ使用量の削減
- **Base64画像埋め込み機能の統合**: CLI版でも同等の機能を提供
- **ファイル命名の明確化**: `my-memoir-cli.pdf` でエンジンを識別

### ⚠️ 構造上の課題
- **PDF生成の使い分け** - Puppeteer版（汎用）とCLI版（自分史専用）の併用
- **ユーティリティの未使用** - 高機能なヘルパー関数の部分利用
- **テスト構造の分散** - `tests/` と `scripts/` の混在

## プロジェクト構造

```
auto-designer/
├── src/                           # ソースコード（TypeScript）
│   ├── index.ts                   # 🎯 メインエントリーポイント（Fastify HTTP API）
│   ├── pdf.ts                     # 🔧 PDF生成（Puppeteer + Paged.js）- 汎用
│   ├── pdf-cli.ts                 # ✅ PDF生成（pagedjs-cli）- 自分史専用
│   ├── types/                     
│   │   └── index.ts               # ✅ 型定義（全テンプレート対応）
│   ├── utils/                     
│   │   ├── image-manager.ts       # 🔧 画像管理（高機能だが部分利用）
│   │   ├── template-utils.ts      # ❌ テンプレートヘルパー（未使用）
│   │   └── file-utils.ts          # 🔧 ファイル操作（部分利用）
│   └── templates/                 # ETAテンプレート
│       ├── magazine.eta           # ✅ 雑誌テンプレート（Puppeteer版）
│       ├── invoice.eta            # ✅ 請求書テンプレート（Puppeteer版）
│       └── memoir.eta             # ✅ 自分史テンプレート（CLI版）
├── samples/                       # サンプルデータ
│   ├── magazine-sample.json       # ✅ 雑誌サンプル
│   ├── invoice-sample.json        # ✅ 請求書サンプル
│   ├── memoir-sample.json         # ✅ 自分史サンプル
│   └── memoir-sample.html         # ✅ 自分史作成ツール（CLI版対応）
├── uploads/                       # アップロード画像（9ファイル、合計20MB）
├── output/                        # 生成PDF（1ファイル、28MB）
├── test-output/                   # テスト出力（2ファイル）
├── tests/                         # テストファイル（HTML形式）
├── scripts/                       # スクリプト（Shell）
├── docs/                          # 設計ドキュメント
└── temp/                          # 一時ファイル（空）
```

## 使用方法

### インストール
```bash
npm install
```

### 開発
```bash
npm run dev
```

### テスト
```bash
npm test
```

### PDF生成
```bash
npm run build
node dist/index.js
```

## 機能

### 基本機能
- 雑誌形式のPDF自動生成
- 請求書形式のPDF自動生成
- 自分史形式のPDF自動生成（**年表レイアウト + 画像埋め込み**）
- ETAテンプレートエンジン使用
- TypeScript対応
- CLI対応

### 画像機能
- 画像アップロード（Base64エンコード）
- 画像最適化（Sharp使用）
- 画像表示エンドポイント
- 画像一覧取得
- **Base64埋め込みによるファイルサイズ最適化** - 98%削減実績

### 自分史機能
- 年表形式のレイアウト
- プロフィール情報表示
- 画像付きイベント記録
- HTMLプレビュー機能
- PDF出力機能
- **9つの人生イベント画像対応**

## API エンドポイント

### 基本エンドポイント
- `GET /health` - ヘルスチェック
- `GET /templates` - 利用可能なテンプレート一覧
- `POST /pdf` - PDF生成（Puppeteer版）- 汎用テンプレート用
- `POST /pdf/cli` - PDF生成（pagedjs-cli版）- **自分史専用**

### 画像関連エンドポイント
- `POST /upload/image` - 画像アップロード
- `GET /images` - 画像一覧取得
- `GET /images/:fileName` - 画像表示

### 自分史関連エンドポイント
- `POST /memoir/preview` - 自分史HTMLプレビュー

## 自分史作成ツール

`samples/memoir-sample.html` をブラウザで開くと、自分史作成ツールを使用できます。

### 機能
- 基本情報入力（名前、生年月日、職業など）
- 年表項目の追加・編集
- 画像URLの設定
- リアルタイムプレビュー
- **PDF出力（pagedjs-cli版）**

### 使用例
1. サーバーを起動: `npm run dev`
2. ブラウザで `samples/memoir-sample.html` を開く
3. 情報を入力してプレビュー
4. **pagedjs-cli版でPDFを生成してダウンロード**

## テンプレート

### 自分史テンプレート（memoir.eta）
- 表紙ページ
- 目次
- プロフィールセクション
- 年表レイアウト
- 画像表示対応
- 印刷用スタイル

### データ構造
```json
{
  "title": "タイトル",
  "subtitle": "サブタイトル",
  "author": "著者名",
  "birthDate": "生年月日",
  "birthPlace": "出身地",
  "occupation": "職業",
  "interests": ["趣味1", "趣味2"],
  "motto": "座右の銘",
  "profileImage": "プロフィール画像URL",
  "timeline": [
    {
      "year": 1985,
      "title": "イベントタイトル",
      "description": "説明",
      "image": "画像URL",
      "imageCaption": "画像キャプション"
    }
  ]
}
```

## パフォーマンス実績

### Base64画像埋め込み最適化（両版共通）
- **Before**: 29.7MB PDF
- **After**: 407KB PDF（**98%削減**）
- **処理時間**: 3.9秒 → 3.1秒（**20%改善**）
- **ネットワーク依存**: 完全解消

### pagedjs-cli版の追加メリット
- **メモリ使用量**: Puppeteer版より約30%削減
- **プロセス安定性**: CLI実行による独立したプロセス
- **デバッグ性**: コマンドライン出力による問題の特定が容易

## 最適化推奨事項

### 短期的改善
1. **PDF生成の用途別最適化** - 用途に応じたエンジン選択の指針作成
2. **未使用コードの削除** - template-utils.ts等
3. **テスト構造の整理** - Jest導入

### 長期的改善
1. **型安全性の向上** - 全型定義の完備
2. **ファイル管理の改善** - 出力ディレクトリの統一
3. **ドキュメントの整備** - API仕様書の更新
4. **パフォーマンス監視** - 各エンジンの使用状況追跡 