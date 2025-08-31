# モダンテンプレート集

新しく作成されたモダンで美しいデザインのテンプレート集です。デザインを少しずつ磨いていくプロトタイピングに最適です。

## 🎨 利用可能なテンプレート

### 1. モダンミニマル片面ページ
- **パス**: `single/modern-minimal-single/`
- **特徴**: シンプルで洗練された片面ページ
- **用途**: 記事ページ、紹介ページ
- **デザイン要素**: グラデーション背景、装飾円、モダンなタイポグラフィ

### 2. モダンバランス見開きページ
- **パス**: `spread/modern-balanced-spread/`
- **特徴**: 左右のバランスが取れた見開きレイアウト
- **用途**: 特集ページ、長文記事
- **デザイン要素**: 左右非対称レイアウト、引用セクション、装飾線

### 3. モダンタイトルページ
- **パス**: `title/modern-title-page/`
- **特徴**: 印象的なグラデーション背景のタイトルページ
- **用途**: マガジンの表紙、特集の開始ページ
- **デザイン要素**: グラデーション背景、装飾要素、透明効果

## 🚀 使用方法

### 1. テンプレートの確認
```bash
cd vivliostyle
python test-modern-templates.py
```

### 2. ブラウザでの確認
各テンプレートのHTMLファイルをブラウザで開いてデザインを確認できます。

### 3. CSSの調整
`style.css`ファイルを編集して、以下の要素を調整できます：

#### 色の変更
```css
/* メインカラー */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* テキストカラー */
color: #2d3748;
```

#### フォントサイズの調整
```css
.main-title {
    font-size: 48px; /* この値を変更 */
}
```

#### レイアウトの微調整
```css
.page {
    padding: 40mm 30mm; /* 余白を調整 */
}
```

## 🖨️ PDFビルド

### Vivliostyle CLIのインストール
```bash
npm install -g @vivliostyle/cli
```

### 個別テンプレートのPDF生成
```bash
# タイトルページ
vivliostyle build sample/templates/title/modern-title-page/index.html -o output/title-page.pdf

# 片面ページ
vivliostyle build sample/templates/single/modern-minimal-single/index.html -o output/single-page.pdf

# 見開きページ
vivliostyle build sample/templates/spread/modern-balanced-spread/index.html -o output/spread-page.pdf
```

### 統合PDFの生成
```bash
vivliostyle build vivliostyle.config.js
```

### 自動化スクリプトの使用
```bash
# シェルスクリプト
./build-pdf.sh

# Pythonスクリプト
python test-modern-templates.py
# メニューから「2. PDFをビルド」を選択
```

## ⚙️ Vivliostyle設定

### 設定ファイル (`vivliostyle.config.js`)
- **サイズ**: A4
- **言語**: 日本語
- **目次**: 有効
- **印刷最適化**: 有効

### カスタマイズ可能な設定
```javascript
module.exports = {
  title: "モダンテンプレート集",
  author: "デザイン研究家",
  language: "ja",
  size: "A4",
  theme: "@vivliostyle/theme-base",
  entry: [
    // エントリーファイルのリスト
  ],
  output: [
    "output/modern-templates.pdf"
  ],
  toc: true,
  print: true
};
```

## 🔧 デザイン調整のポイント

### 段階的な改善
1. **基本レイアウト**: まずは要素の配置を決める
2. **色とタイポグラフィ**: カラーパレットとフォントを調整
3. **装飾要素**: 背景やアクセントを追加
4. **微調整**: 細かいスペーシングやサイズを調整

### よく使うCSSプロパティ
- `margin`, `padding`: スペーシング
- `font-size`, `line-height`: タイポグラフィ
- `background`, `color`: 色と背景
- `border-radius`, `box-shadow`: 装飾効果
- `position`, `z-index`: レイアウト制御

## 📱 レスポンシブ対応

各テンプレートは印刷用に最適化されていますが、必要に応じてレスポンシブ対応も可能です：

```css
@media screen and (max-width: 768px) {
    .page {
        padding: 20mm 15mm;
    }
    
    .main-title {
        font-size: 32px;
    }
}
```

## 🎯 カスタマイズ例

### 色テーマの変更
```css
/* 暖色系テーマ */
:root {
    --primary-color: #f56565;
    --secondary-color: #ed8936;
    --accent-color: #ecc94b;
}

/* 寒色系テーマ */
:root {
    --primary-color: #4299e1;
    --secondary-color: #38b2ac;
    --accent-color: #9f7aea;
}
```

### 装飾要素の追加
```css
/* 新しい装飾要素 */
.decoration-dot {
    position: absolute;
    width: 8px;
    height: 8px;
    background: var(--accent-color);
    border-radius: 50%;
    opacity: 0.6;
}
```

## 📚 参考資料

- [CSS Grid Layout](https://developer.mozilla.org/ja/docs/Web/CSS/CSS_Grid_Layout)
- [CSS Flexbox](https://developer.mozilla.org/ja/docs/Web/CSS/CSS_Flexible_Box_Layout)
- [CSS Gradients](https://developer.mozilla.org/ja/docs/Web/CSS/gradient)
- [CSS Box Shadow](https://developer.mozilla.org/ja/docs/Web/CSS/box-shadow)
- [Vivliostyle Documentation](https://vivliostyle.org/)

## 🤝 貢献

新しいテンプレートやデザインの改善案があれば、ぜひ共有してください！

---

**注意**: これらのテンプレートは学習・プロトタイピング用です。商用利用の際は適切なライセンス確認をお願いします。
