#!/bin/bash

# Paged.js PDF WebAPI テストスクリプト
# 使用方法: ./test.sh

BASE_URL="http://localhost:3000"
OUTPUT_DIR="./test-output"

# 出力ディレクトリを作成
mkdir -p $OUTPUT_DIR

echo "🚀 Paged.js PDF WebAPI テスト開始"
echo "=================================="

# ヘルスチェック
echo "📋 ヘルスチェック..."
curl -s "$BASE_URL/health" | jq .
echo ""

# テンプレート一覧取得
echo "📝 テンプレート一覧取得..."
curl -s "$BASE_URL/templates" | jq .
echo ""

# 請求書PDF生成テスト
echo "📄 請求書PDF生成テスト..."
curl -X POST "$BASE_URL/pdf" \
  -H "Content-Type: application/json" \
  --data @samples/invoice-sample.json \
  --output "$OUTPUT_DIR/invoice.pdf" \
  -w "処理時間: %{time_total}s, ステータス: %{http_code}\n"
echo ""

# 雑誌PDF生成テスト
echo "📚 雑誌PDF生成テスト..."
curl -X POST "$BASE_URL/pdf" \
  -H "Content-Type: application/json" \
  --data @samples/magazine-sample.json \
  --output "$OUTPUT_DIR/magazine.pdf" \
  -w "処理時間: %{time_total}s, ステータス: %{http_code}\n"
echo ""

# エラーテスト（存在しないテンプレート）
echo "❌ エラーテスト（存在しないテンプレート）..."
curl -X POST "$BASE_URL/pdf" \
  -H "Content-Type: application/json" \
  -d '{"template": "not-exists", "data": {}}' \
  -w "ステータス: %{http_code}\n"
echo ""

# 生成されたPDFファイルの確認
echo "📁 生成されたファイル:"
ls -la $OUTPUT_DIR/
echo ""

echo "✅ テスト完了！"
echo "生成されたPDFファイルは $OUTPUT_DIR/ ディレクトリに保存されています。" 