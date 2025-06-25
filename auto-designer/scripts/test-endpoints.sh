#!/bin/bash

# Paged.js PDF WebAPI エンドポイント別テストスクリプト
# 使用方法: ./test-endpoints.sh [endpoint_name]
# 例: ./test-endpoints.sh health
# 例: ./test-endpoints.sh all

BASE_URL="http://localhost:3000"
OUTPUT_DIR="./test-output"
SAMPLES_DIR="./samples"

# 出力ディレクトリを作成
mkdir -p $OUTPUT_DIR

# 色付きログ関数
log_info() {
    echo "🔵 $1"
}

log_success() {
    echo "✅ $1"
}

log_error() {
    echo "❌ $1"
}

log_warning() {
    echo "⚠️ $1"
}

log_section() {
    echo ""
    echo "=========================================="
    echo "📋 $1"
    echo "=========================================="
}

# ヘルスチェックテスト
test_health() {
    log_section "ヘルスチェックテスト"
    log_info "GET /health"
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$BASE_URL/health")
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo $response | sed -e 's/HTTPSTATUS\:.*//g')
    
    if [ "$http_code" -eq 200 ]; then
        log_success "ヘルスチェック成功 (HTTP $http_code)"
        echo "$body" | jq . 2>/dev/null || echo "$body"
    else
        log_error "ヘルスチェック失敗 (HTTP $http_code)"
        echo "$body"
    fi
}

# v2 ヘルスチェックテスト
test_v2_health() {
    log_section "v2 ヘルスチェックテスト"
    log_info "GET /v2/health"
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$BASE_URL/v2/health")
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo $response | sed -e 's/HTTPSTATUS\:.*//g')
    
    if [ "$http_code" -eq 200 ]; then
        log_success "v2 ヘルスチェック成功 (HTTP $http_code)"
        echo "$body" | jq . 2>/dev/null || echo "$body"
    else
        log_error "v2 ヘルスチェック失敗 (HTTP $http_code)"
        echo "$body"
    fi
}

# テンプレート一覧取得テスト
test_templates() {
    log_section "テンプレート一覧取得テスト"
    log_info "GET /templates"
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$BASE_URL/templates")
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo $response | sed -e 's/HTTPSTATUS\:.*//g')
    
    if [ "$http_code" -eq 200 ]; then
        log_success "テンプレート一覧取得成功 (HTTP $http_code)"
        echo "$body" | jq . 2>/dev/null || echo "$body"
    else
        log_error "テンプレート一覧取得失敗 (HTTP $http_code)"
        echo "$body"
    fi
}

# v2 テンプレート情報取得テスト
test_v2_templates() {
    log_section "v2 テンプレート情報取得テスト"
    log_info "GET /v2/templates"
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$BASE_URL/v2/templates")
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo $response | sed -e 's/HTTPSTATUS\:.*//g')
    
    if [ "$http_code" -eq 200 ]; then
        log_success "v2 テンプレート情報取得成功 (HTTP $http_code)"
        echo "$body" | jq . 2>/dev/null || echo "$body"
    else
        log_error "v2 テンプレート情報取得失敗 (HTTP $http_code)"
        echo "$body"
    fi
}

# v2 サンプルデータ取得テスト
test_v2_samples() {
    log_section "v2 サンプルデータ取得テスト"
    log_info "GET /v2/samples/memoir"
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$BASE_URL/v2/samples/memoir")
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo $response | sed -e 's/HTTPSTATUS\:.*//g')
    
    if [ "$http_code" -eq 200 ]; then
        log_success "v2 サンプルデータ取得成功 (HTTP $http_code)"
        echo "$body" | jq . 2>/dev/null || echo "$body"
    else
        log_error "v2 サンプルデータ取得失敗 (HTTP $http_code)"
        echo "$body"
    fi
}

# 画像アップロードテスト
test_image_upload() {
    log_section "画像アップロードテスト"
    log_info "POST /upload/image"
    
    # テスト用の小さな画像データ（1x1ピクセルのPNG）
    test_image_data="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X POST "$BASE_URL/upload/image" \
        -H "Content-Type: application/json" \
        -d "{\"imageData\": \"$test_image_data\", \"fileName\": \"test-image.png\", \"mimeType\": \"image/png\"}")
    
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo $response | sed -e 's/HTTPSTATUS\:.*//g')
    
    if [ "$http_code" -eq 200 ]; then
        log_success "画像アップロード成功 (HTTP $http_code)"
        echo "$body" | jq . 2>/dev/null || echo "$body"
    else
        log_error "画像アップロード失敗 (HTTP $http_code)"
        echo "$body"
    fi
}

# 画像一覧取得テスト
test_images() {
    log_section "画像一覧取得テスト"
    log_info "GET /images"
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$BASE_URL/images")
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo $response | sed -e 's/HTTPSTATUS\:.*//g')
    
    if [ "$http_code" -eq 200 ]; then
        log_success "画像一覧取得成功 (HTTP $http_code)"
        echo "$body" | jq . 2>/dev/null || echo "$body"
    else
        log_error "画像一覧取得失敗 (HTTP $http_code)"
        echo "$body"
    fi
}

# 自分史プレビューテスト
test_memoir_preview() {
    log_section "自分史プレビューテスト"
    log_info "POST /memoir/preview"
    
    if [ ! -f "$SAMPLES_DIR/memoir-sample.json" ]; then
        log_error "サンプルファイルが見つかりません: $SAMPLES_DIR/memoir-sample.json"
        return 1
    fi
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X POST "$BASE_URL/memoir/preview" \
        -H "Content-Type: application/json" \
        --data @$SAMPLES_DIR/memoir-sample.json)
    
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo $response | sed -e 's/HTTPSTATUS\:.*//g')
    
    if [ "$http_code" -eq 200 ]; then
        log_success "自分史プレビュー生成成功 (HTTP $http_code)"
        echo "HTMLプレビューが生成されました（長いため省略）"
        echo "HTMLサイズ: $(echo "$body" | wc -c) bytes"
    else
        log_error "自分史プレビュー生成失敗 (HTTP $http_code)"
        echo "$body"
    fi
}

# PDF生成テスト（puppeteer版）
test_pdf_puppeteer() {
    log_section "PDF生成テスト（puppeteer版）"
    log_info "POST /pdf"
    
    if [ ! -f "$SAMPLES_DIR/invoice-sample.json" ]; then
        log_error "サンプルファイルが見つかりません: $SAMPLES_DIR/invoice-sample.json"
        return 1
    fi
    
    start_time=$(date +%s.%N)
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X POST "$BASE_URL/pdf" \
        -H "Content-Type: application/json" \
        --data @$SAMPLES_DIR/invoice-sample.json \
        --output "$OUTPUT_DIR/invoice-puppeteer.pdf")
    
    end_time=$(date +%s.%N)
    processing_time=$(echo "$end_time - $start_time" | bc)
    
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    
    if [ "$http_code" -eq 200 ]; then
        log_success "PDF生成成功（puppeteer版） (HTTP $http_code)"
        log_info "処理時間: ${processing_time}秒"
        if [ -f "$OUTPUT_DIR/invoice-puppeteer.pdf" ]; then
            file_size=$(stat -f%z "$OUTPUT_DIR/invoice-puppeteer.pdf" 2>/dev/null || stat -c%s "$OUTPUT_DIR/invoice-puppeteer.pdf" 2>/dev/null || echo "unknown")
            log_info "ファイルサイズ: ${file_size} bytes"
        fi
    else
        log_error "PDF生成失敗（puppeteer版） (HTTP $http_code)"
        echo "$response"
    fi
}

# PDF生成テスト（pagedjs-cli版）
test_pdf_cli() {
    log_section "PDF生成テスト（pagedjs-cli版）"
    log_info "POST /pdf/cli"
    
    if [ ! -f "$SAMPLES_DIR/invoice-sample.json" ]; then
        log_error "サンプルファイルが見つかりません: $SAMPLES_DIR/invoice-sample.json"
        return 1
    fi
    
    start_time=$(date +%s.%N)
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X POST "$BASE_URL/pdf/cli" \
        -H "Content-Type: application/json" \
        --data @$SAMPLES_DIR/invoice-sample.json \
        --output "$OUTPUT_DIR/invoice-cli.pdf")
    
    end_time=$(date +%s.%N)
    processing_time=$(echo "$end_time - $start_time" | bc)
    
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    
    if [ "$http_code" -eq 200 ]; then
        log_success "PDF生成成功（pagedjs-cli版） (HTTP $http_code)"
        log_info "処理時間: ${processing_time}秒"
        if [ -f "$OUTPUT_DIR/invoice-cli.pdf" ]; then
            file_size=$(stat -f%z "$OUTPUT_DIR/invoice-cli.pdf" 2>/dev/null || stat -c%s "$OUTPUT_DIR/invoice-cli.pdf" 2>/dev/null || echo "unknown")
            log_info "ファイルサイズ: ${file_size} bytes"
        fi
    else
        log_error "PDF生成失敗（pagedjs-cli版） (HTTP $http_code)"
        echo "$response"
    fi
}

# v2 PDF生成テスト
test_v2_pdf() {
    log_section "v2 PDF生成テスト"
    log_info "POST /v2/pdf"
    
    # 最小限の有効なmemoirデータを作成
    memoir_data='{
      "template": "memoir",
      "data": {
        "title": "テスト自分史",
        "author": "テスト太郎",
        "profile": {
          "name": "テスト太郎",
          "birthDate": "1990年1月1日",
          "description": "テスト用の自分史です"
        },
        "timeline": [
          {
            "year": 1990,
            "title": "誕生",
            "description": "テスト用の誕生イベントです"
          }
        ]
      }
    }'
    
    start_time=$(date +%s.%N)
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X POST "$BASE_URL/v2/pdf" \
        -H "Content-Type: application/json" \
        -d "$memoir_data" \
        --output "$OUTPUT_DIR/memoir-v2.pdf")
    
    end_time=$(date +%s.%N)
    processing_time=$(echo "$end_time - $start_time" | bc)
    
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    
    if [ "$http_code" -eq 200 ]; then
        log_success "v2 PDF生成成功 (HTTP $http_code)"
        log_info "処理時間: ${processing_time}秒"
        if [ -f "$OUTPUT_DIR/memoir-v2.pdf" ]; then
            file_size=$(stat -f%z "$OUTPUT_DIR/memoir-v2.pdf" 2>/dev/null || stat -c%s "$OUTPUT_DIR/memoir-v2.pdf" 2>/dev/null || echo "unknown")
            log_info "ファイルサイズ: ${file_size} bytes"
        fi
    else
        log_error "v2 PDF生成失敗 (HTTP $http_code)"
        echo "$response"
    fi
}

# v2 エラーテスト
test_v2_errors() {
    log_section "v2 エラーテスト"
    
    # テンプレートが指定されていない場合
    log_info "テンプレートが指定されていない場合"
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X POST "$BASE_URL/v2/pdf" \
        -H "Content-Type: application/json" \
        -d '{"data": {"title": "テスト", "author": "テスト"}}')
    
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo $response | sed -e 's/HTTPSTATUS\:.*//g')
    
    if [ "$http_code" -eq 400 ]; then
        log_success "v2 エラーハンドリング正常 (HTTP $http_code)"
        echo "$body" | jq . 2>/dev/null || echo "$body"
    else
        log_warning "予期しないv2レスポンス (HTTP $http_code)"
        echo "$body"
    fi
    
    # サポートされていないテンプレート
    log_info "サポートされていないテンプレート"
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X POST "$BASE_URL/v2/pdf" \
        -H "Content-Type: application/json" \
        -d '{"template": "unsupported", "data": {"title": "テスト", "author": "テスト"}}')
    
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo $response | sed -e 's/HTTPSTATUS\:.*//g')
    
    if [ "$http_code" -eq 400 ]; then
        log_success "v2 サポート外テンプレートエラー正常 (HTTP $http_code)"
        echo "$body" | jq . 2>/dev/null || echo "$body"
    else
        log_warning "予期しないv2レスポンス (HTTP $http_code)"
        echo "$body"
    fi
}

# ChatGPTテスト
test_chat() {
    log_section "ChatGPTテスト"
    log_info "POST /chat"
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X POST "$BASE_URL/chat" \
        -H "Content-Type: application/json" \
        -d '{
            "prompt": "こんにちは！簡単な挨拶をしてください。",
            "model": "gpt-3.5-turbo"
        }')
    
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo $response | sed -e 's/HTTPSTATUS\:.*//g')
    
    if [ "$http_code" -eq 200 ]; then
        log_success "ChatGPT呼び出し成功 (HTTP $http_code)"
        echo "$body" | jq . 2>/dev/null || echo "$body"
    else
        log_error "ChatGPT呼び出し失敗 (HTTP $http_code)"
        echo "$body"
    fi
}

# チャットボットテスト
test_chatbot() {
    log_section "チャットボットテスト"
    log_info "POST /chatbot"
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X POST "$BASE_URL/chatbot" \
        -H "Content-Type: application/json" \
        -d '{
            "initialPrompt": "今日の天気について教えてください。",
            "maxTurns": 3
        }')
    
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo $response | sed -e 's/HTTPSTATUS\:.*//g')
    
    if [ "$http_code" -eq 200 ]; then
        log_success "チャットボット実行成功 (HTTP $http_code)"
        echo "$body" | jq . 2>/dev/null || echo "$body"
    else
        log_error "チャットボット実行失敗 (HTTP $http_code)"
        echo "$body"
    fi
}

# エラーテスト
test_errors() {
    log_section "エラーテスト"
    
    # 存在しないテンプレートでのPDF生成
    log_info "存在しないテンプレートでのPDF生成"
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X POST "$BASE_URL/pdf" \
        -H "Content-Type: application/json" \
        -d '{"template": "not-exists", "data": {}}')
    
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo $response | sed -e 's/HTTPSTATUS\:.*//g')
    
    if [ "$http_code" -eq 400 ]; then
        log_success "エラーハンドリング正常 (HTTP $http_code)"
        echo "$body" | jq . 2>/dev/null || echo "$body"
    else
        log_warning "予期しないレスポンス (HTTP $http_code)"
        echo "$body"
    fi
    
    # 存在しないエンドポイント
    log_info "存在しないエンドポイント"
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$BASE_URL/not-exists")
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    
    if [ "$http_code" -eq 404 ]; then
        log_success "404エラーハンドリング正常 (HTTP $http_code)"
    else
        log_warning "予期しない404レスポンス (HTTP $http_code)"
    fi
}

# ファイル確認
check_generated_files() {
    log_section "生成されたファイル確認"
    
    if [ -d "$OUTPUT_DIR" ]; then
        log_info "出力ディレクトリ: $OUTPUT_DIR"
        ls -la "$OUTPUT_DIR/"
        
        echo ""
        log_info "PDFファイルサイズ確認:"
        for file in "$OUTPUT_DIR"/*.pdf; do
            if [ -f "$file" ]; then
                size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "unknown")
                echo "  $(basename "$file"): ${size} bytes"
            fi
        done
    else
        log_warning "出力ディレクトリが存在しません: $OUTPUT_DIR"
    fi
}

# メイン処理
main() {
    echo "🚀 Paged.js PDF WebAPI エンドポイント別テスト開始"
    echo "=========================================="
    echo "ベースURL: $BASE_URL"
    echo "出力ディレクトリ: $OUTPUT_DIR"
    echo ""
    
    case "${1:-all}" in
        "health")
            test_health
            ;;
        "v2-health")
            test_v2_health
            ;;
        "templates")
            test_templates
            ;;
        "v2-templates")
            test_v2_templates
            ;;
        "v2-samples")
            test_v2_samples
            ;;
        "upload")
            test_image_upload
            ;;
        "images")
            test_images
            ;;
        "preview")
            test_memoir_preview
            ;;
        "pdf")
            test_pdf_puppeteer
            ;;
        "pdf-cli")
            test_pdf_cli
            ;;
        "v2-pdf")
            test_v2_pdf
            ;;
        "v2-errors")
            test_v2_errors
            ;;
        "chat")
            test_chat
            ;;
        "chatbot")
            test_chatbot
            ;;
        "errors")
            test_errors
            ;;
        "files")
            check_generated_files
            ;;
        "v2")
            test_v2_health
            test_v2_templates
            test_v2_samples
            test_v2_pdf
            test_v2_errors
            ;;
        "all")
            test_health
            test_v2_health
            test_templates
            test_v2_templates
            test_v2_samples
            test_image_upload
            test_images
            test_memoir_preview
            test_pdf_puppeteer
            test_pdf_cli
            test_v2_pdf
            test_v2_errors
            test_chat
            test_chatbot
            test_errors
            check_generated_files
            ;;
        *)
            echo "使用方法: $0 [endpoint_name]"
            echo ""
            echo "利用可能なテスト:"
            echo "  health       - ヘルスチェック"
            echo "  v2-health    - v2 ヘルスチェック"
            echo "  templates    - テンプレート一覧取得"
            echo "  v2-templates - v2 テンプレート情報取得"
            echo "  v2-samples   - v2 サンプルデータ取得"
            echo "  upload       - 画像アップロード"
            echo "  images       - 画像一覧取得"
            echo "  preview      - 自分史プレビュー"
            echo "  pdf          - PDF生成（puppeteer版）"
            echo "  pdf-cli      - PDF生成（pagedjs-cli版）"
            echo "  v2-pdf       - v2 PDF生成"
            echo "  v2-errors    - v2 エラーテスト"
            echo "  chat         - ChatGPT"
            echo "  chatbot      - チャットボット"
            echo "  errors       - エラーテスト"
            echo "  files        - 生成ファイル確認"
            echo "  v2           - v2 API全テスト"
            echo "  all          - 全テスト実行（デフォルト）"
            exit 1
            ;;
    esac
    
    echo ""
    log_success "テスト完了！"
}

# スクリプト実行
main "$@" 