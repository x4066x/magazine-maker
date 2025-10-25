# Vivliostyle オプション設定ガイド

## 🎨 概要

Vivliostyle CLIのオプションを柔軟に指定できるようになりました！

PDF生成時に、サイズ、フォーマット、トンボ、裁ち落としなどを自由にカスタマイズできます。

## 📋 利用可能なオプション

### 基本オプション

| オプション | 型 | デフォルト | 説明 |
|---------|---|----------|------|
| `format` | str | `"pdf"` | 出力フォーマット（pdf） |
| `size` | str | `"A4"` | 用紙サイズ（A4, A5, B5, letter, など） |
| `single_doc` | bool | `True` | 単一ドキュメントとして出力 |
| `timeout` | int | `90` | タイムアウト時間（秒） |

### 印刷用オプション

| オプション | 型 | デフォルト | 説明 |
|---------|---|----------|------|
| `crop_marks` | bool | `False` | トンボ（crop marks）を表示 |
| `bleed` | str | なし | 裁ち落とし幅（例: "3mm"） |

### 高度なオプション

| オプション | 型 | デフォルト | 説明 |
|---------|---|----------|------|
| `css` | str | なし | 追加CSSファイルのパス |

## 🚀 使い方

### 1. デフォルト設定で生成

```python
from app.services.quick_memoir_service import quick_memoir_service

# デフォルト設定（A4, タイムアウト90秒）
pdf_result = quick_memoir_service.generate_quick_pdf(session)
```

### 2. カスタムサイズで生成

```python
# B5サイズで生成
pdf_result = quick_memoir_service.generate_quick_pdf(
    session,
    vivliostyle_options={
        "size": "B5"
    }
)
```

### 3. 印刷用に生成（トンボ + 裁ち落とし）

```python
# 印刷業者向け設定
pdf_result = quick_memoir_service.generate_quick_pdf(
    session,
    vivliostyle_options={
        "size": "A4",
        "crop_marks": True,    # トンボを表示
        "bleed": "3mm",        # 3mmの裁ち落とし
        "timeout": 120         # タイムアウト2分
    }
)
```

### 4. カスタムCSSを適用

```python
# 追加のCSSスタイルを適用
pdf_result = quick_memoir_service.generate_quick_pdf(
    session,
    vivliostyle_options={
        "size": "A4",
        "css": "/path/to/custom.css"
    }
)
```

## 📐 用紙サイズ一覧

### ISO A系列
- `A3` - 297mm × 420mm
- `A4` - 210mm × 297mm（デフォルト）
- `A5` - 148mm × 210mm
- `A6` - 105mm × 148mm

### ISO B系列
- `B4` - 250mm × 353mm
- `B5` - 176mm × 250mm
- `B6` - 125mm × 176mm

### その他
- `letter` - 8.5in × 11in（USレター）
- `legal` - 8.5in × 14in（USリーガル）
- `ledger` - 11in × 17in

### カスタムサイズ
```python
vivliostyle_options={
    "size": "210mm,297mm"  # 幅,高さ
}
```

## 🖨️ 印刷用設定例

### 家庭用プリンター向け
```python
{
    "size": "A4",
    "format": "pdf"
}
```

### 印刷業者向け（オフセット印刷）
```python
{
    "size": "A4",
    "crop_marks": True,   # トンボ表示
    "bleed": "3mm",       # 裁ち落とし3mm
    "timeout": 120
}
```

### 小冊子向け
```python
{
    "size": "A5",
    "format": "pdf",
    "timeout": 90
}
```

## 🎨 カスタムCSS例

追加のスタイルを適用する場合：

### custom.css
```css
/* フォントを変更 */
body {
    font-family: 'Noto Serif JP', serif;
}

/* ヘッダーの色を変更 */
.section-title {
    color: #e74c3c;
}

/* 余白を調整 */
@page {
    margin: 15mm;
}
```

使用方法：
```python
vivliostyle_options={
    "size": "A4",
    "css": "path/to/custom.css"
}
```

## 🔧 デフォルト設定の変更

`app/services/quick_memoir_service.py` で設定：

```python
# デフォルトのVivliostyleオプション
if vivliostyle_options is None:
    vivliostyle_options = {
        "size": "A4",           # お好みのサイズに変更
        "format": "pdf",
        "single_doc": True,
        "timeout": 90           # タイムアウト時間を調整
    }
```

## 📊 タイムアウト設定の目安

| 内容 | 推奨タイムアウト |
|-----|--------------|
| テキストのみ | 30秒 |
| 画像1〜3枚 | 60秒 |
| 画像4〜10枚 | 90秒（デフォルト） |
| 画像11枚以上 | 120秒〜180秒 |

## 🐛 トラブルシューティング

### タイムアウトエラーが発生する

```python
# タイムアウトを延長
vivliostyle_options={
    "timeout": 180  # 3分
}
```

### 用紙サイズが反映されない

- サイズ名を確認（大文字小文字を区別）
- カスタムサイズの場合は `"幅,高さ"` 形式で指定

### トンボが表示されない

```python
# crop_marksオプションを有効化
vivliostyle_options={
    "crop_marks": True,
    "bleed": "3mm"  # 裁ち落としも設定
}
```

## 📚 Vivliostyle CLI ドキュメント

詳細は公式ドキュメントを参照：
- [Vivliostyle CLI](https://docs.vivliostyle.org/#/cli)
- [Page Size Specification](https://www.w3.org/TR/css-page-3/#page-size-prop)

## 🎉 まとめ

Vivliostyleオプションを活用することで：

✅ 様々な用紙サイズに対応  
✅ 印刷業者への入稿データ作成  
✅ カスタムスタイルの適用  
✅ タイムアウト時間の最適化  

柔軟なPDF生成が可能になりました！

