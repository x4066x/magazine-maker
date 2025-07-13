# マガジンメーカープロジェクト 設計ドキュメント

## プロジェクト概要
マガジン制作を自動化するシステムの設計ドキュメントです。

## ディレクトリ構成

```
magazine-maker/
├── vivliostyle/           # VivliostyleによるPDF生成
│   └── sample/
│       ├── templates/     # テンプレート分類（新規追加）
│       │   ├── title/     # タイトルページ
│       │   ├── spread/    # 見開きページ
│       │   └── single/    # 片面ページ
│       └── [元のテンプレート]
├── template-editor/       # テンプレート編集ツール
├── line-bot/             # LINE Bot連携
├── auto-designer/        # 自動デザイン生成
└── auto-print/           # 自動印刷システム
```

## テンプレート分類システム

### 更新日: 2024年12月
### 更新内容: テンプレートの用途別分類と名前変更

#### 分類基準
1. **タイトルページ**: マガジンのタイトルと著者名を表示
2. **見開きページ**: 2ページ構成のレイアウト
3. **片面ページ**: 1ページ構成のレイアウト

#### 詳細分類

##### 1. タイトルページ (title/)
- **title-page**: 背景画像 + タイトル + 著者名
  - 用途: メインタイトルページ
  - 特徴: シンプルで印象的なデザイン

##### 2. 見開きページ (spread/)
- **quote-spread**: 左ページ（画像+引用）、右ページ（空白）
- **text-image-spread**: 左ページ（本文3段）、右ページ（画像）
- **balanced-spread**: 左ページ（画像+本文）、右ページ（本文3段）
- **dual-image-spread**: 両ページ（本文+画像）
- **multi-image-spread**: 左ページ（複数画像+本文）、右ページ（本文）
- **academic-spread**: 左ページ（画像+本文）、右ページ（本文）

##### 3. 片面ページ (single/)
- **image-text-single**: 上部画像 + 下部本文
- **text-only-single**: 本文のみ（3段構成）
- **minimal-single**: 画像 + 短いテキスト
- **text-image-text-single**: 上部本文 + 中部画像 + 下部本文
- **text-focused-single**: 上部本文 + 中部画像 + 下部本文
- **summary-single**: 上部画像 + 下部本文（2段構成）

#### ファイル構成
```
templates/
├── README.md              # 全体説明
├── title/
│   ├── index.md           # タイトルページ説明
│   └── title-page/        # title-pageテンプレート
├── spread/
│   ├── index.md           # 見開きページ説明
│   ├── quote-spread/      # quote-spreadテンプレート
│   ├── text-image-spread/ # text-image-spreadテンプレート
│   ├── balanced-spread/   # balanced-spreadテンプレート
│   ├── dual-image-spread/ # dual-image-spreadテンプレート
│   ├── multi-image-spread/ # multi-image-spreadテンプレート
│   └── academic-spread/   # academic-spreadテンプレート
└── single/
    ├── index.md           # 片面ページ説明
    ├── image-text-single/ # image-text-singleテンプレート
    ├── text-only-single/  # text-only-singleテンプレート
    ├── minimal-single/    # minimal-singleテンプレート
    ├── text-image-text-single/ # text-image-text-singleテンプレート
    ├── text-focused-single/ # text-focused-singleテンプレート
    └── summary-single/    # summary-singleテンプレート
```

#### 名前変更履歴
- p1 → title-page
- p2-3 → quote-spread
- p4-5 → text-image-spread
- p6-7 → balanced-spread
- p10-11 → dual-image-spread
- p12-13 → multi-image-spread
- p14-15 → academic-spread
- p6 → image-text-single
- p7 → text-only-single
- p8-9 → minimal-single
- p10 → text-image-text-single
- p11 → text-focused-single
- p16 → summary-single

#### 使用方法
1. 使用したいテンプレートのディレクトリをコピー
2. HTMLファイルの内容を編集
3. CSSファイルでスタイルを調整
4. 画像ファイルを適切なディレクトリに配置

#### 技術仕様
- **HTML**: 各テンプレート固有の構造
- **CSS**: 印刷用設定を含むスタイル
- **画像**: `kenji_images/`ディレクトリに配置
- **PDF出力**: Vivliostyleによる高品質なPDF生成

## 今後の開発予定
- テンプレート編集ツールの開発
- 自動レイアウト生成機能
- LINE Bot連携による簡単操作
- 印刷システムとの連携 