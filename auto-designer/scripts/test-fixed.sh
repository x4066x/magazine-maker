#!/bin/bash

# Paged.js PDF WebAPI テストスクリプト（修正版）
# 使用方法: ./test-fixed.sh

BASE_URL="http://localhost:3000"
OUTPUT_DIR="./test-output"

# 出力ディレクトリを作成
mkdir -p $OUTPUT_DIR

echo "🚀 Paged.js PDF WebAPI テスト開始（修正版）"
echo "=========================================="

# ヘルスチェック
echo "📋 ヘルスチェック..."
curl -s "$BASE_URL/health" | jq .
echo ""

# テンプレート一覧取得
echo "📝 テンプレート一覧取得..."
curl -s "$BASE_URL/templates" | jq .
echo ""

# pagedjs-cli版の請求書PDF生成テスト
echo "📄 請求書PDF生成テスト（pagedjs-cli版）..."
curl -X POST "$BASE_URL/pdf/cli" \
  -H "Content-Type: application/json" \
  --data @samples/invoice-sample.json \
  --output "$OUTPUT_DIR/invoice-cli.pdf" \
  -w "処理時間: %{time_total}s, ステータス: %{http_code}\n"
echo ""

# pagedjs-cli版の雑誌PDF生成テスト
echo "📚 雑誌PDF生成テスト（pagedjs-cli版）..."
curl -X POST "$BASE_URL/pdf/cli" \
  -H "Content-Type: application/json" \
  --data @samples/magazine-sample.json \
  --output "$OUTPUT_DIR/magazine-cli.pdf" \
  -w "処理時間: %{time_total}s, ステータス: %{http_code}\n"
echo ""

# エラーテスト（存在しないテンプレート）
echo "❌ エラーテスト（存在しないテンプレート）..."
curl -X POST "$BASE_URL/pdf/cli" \
  -H "Content-Type: application/json" \
  -d '{"template": "not-exists", "data": {}}' \
  -w "ステータス: %{http_code}\n"
echo ""

# 生成されたPDFファイルの確認
echo "📁 生成されたファイル:"
ls -la $OUTPUT_DIR/
echo ""

# PDFファイルのサイズ確認
echo "📊 PDFファイルサイズ確認:"
for file in $OUTPUT_DIR/*.pdf; do
  if [ -f "$file" ]; then
    size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "unknown")
    echo "  $(basename "$file"): ${size} bytes"
  fi
done
echo ""

echo "✅ テスト完了！"
echo "生成されたPDFファイルは $OUTPUT_DIR/ ディレクトリに保存されています。" 