#!/bin/bash

# モダンテンプレートのPDFビルドスクリプト

echo "🎨 モダンテンプレートのPDFビルドを開始します..."

# 出力ディレクトリの作成
mkdir -p output

# 個別テンプレートのPDFビルド
echo "📄 個別テンプレートのPDFを生成中..."

# タイトルページ
echo "  - タイトルページ..."
vivliostyle build sample/templates/modern/title/modern-title-page/index.html -o output/title-page.pdf

# 片面ページ
echo "  - 片面ページ..."
vivliostyle build sample/templates/modern/single/modern-minimal-single/index.html -o output/single-page.pdf

# 見開きページ
echo "  - 見開きページ..."
vivliostyle build sample/templates/modern/spread/modern-balanced-spread/index.html -o output/spread-page.pdf

# 統合PDFのビルド
echo "📚 統合PDFを生成中..."
vivliostyle build vivliostyle.config.js

echo ""
echo "✅ PDFビルドが完了しました！"
echo ""
echo "📁 出力ファイル:"
echo "  - output/title-page.pdf (タイトルページ)"
echo "  - output/single-page.pdf (片面ページ)"
echo "  - output/spread-page.pdf (見開きページ)"
echo "  - output/modern-templates.pdf (統合版)"
echo ""
echo "🔍 ファイルを確認するには:"
echo "  open output/"
