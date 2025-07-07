#!/bin/bash

# 雑誌表紙テンプレートテストスクリプト
# 使用方法: ./test-magazine-covers.sh [template_name]
# 例: ./test-magazine-covers.sh fashion-cover
# 例: ./test-magazine-covers.sh all

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

# ファッション誌表紙テスト
test_fashion_cover() {
    log_section "ファッション誌表紙テスト"
    log_info "POST /v2/pdf (fashion-cover)"
    
    if [ ! -f "$SAMPLES_DIR/fashion-cover-sample.json" ]; then
        log_error "サンプルファイルが見つかりません: $SAMPLES_DIR/fashion-cover-sample.json"
        return 1
    fi
    
    start_time=$(date +%s.%N)
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X POST "$BASE_URL/v2/pdf" \
        -H "Content-Type: application/json" \
        --data @$SAMPLES_DIR/fashion-cover-sample.json \
        --output "$OUTPUT_DIR/fashion-cover.pdf")
    
    end_time=$(date +%s.%N)
    processing_time=$(echo "$end_time - $start_time" | bc)
    
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    
    if [ "$http_code" -eq 200 ]; then
        log_success "ファッション誌表紙PDF生成成功 (HTTP $http_code)"
        log_info "処理時間: ${processing_time}秒"
        if [ -f "$OUTPUT_DIR/fashion-cover.pdf" ]; then
            file_size=$(stat -f%z "$OUTPUT_DIR/fashion-cover.pdf" 2>/dev/null || stat -c%s "$OUTPUT_DIR/fashion-cover.pdf" 2>/dev/null || echo "unknown")
            log_info "ファイルサイズ: ${file_size} bytes"
            log_info "出力ファイル: $OUTPUT_DIR/fashion-cover.pdf"
        fi
    else
        log_error "ファッション誌表紙PDF生成失敗 (HTTP $http_code)"
        echo "$response"
    fi
}

# ライフスタイル誌表紙テスト
test_lifestyle_cover() {
    log_section "ライフスタイル誌表紙テスト"
    log_info "POST /v2/pdf (lifestyle-cover)"
    
    if [ ! -f "$SAMPLES_DIR/lifestyle-cover-sample.json" ]; then
        log_error "サンプルファイルが見つかりません: $SAMPLES_DIR/lifestyle-cover-sample.json"
        return 1
    fi
    
    start_time=$(date +%s.%N)
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X POST "$BASE_URL/v2/pdf" \
        -H "Content-Type: application/json" \
        --data @$SAMPLES_DIR/lifestyle-cover-sample.json \
        --output "$OUTPUT_DIR/lifestyle-cover.pdf")
    
    end_time=$(date +%s.%N)
    processing_time=$(echo "$end_time - $start_time" | bc)
    
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    
    if [ "$http_code" -eq 200 ]; then
        log_success "ライフスタイル誌表紙PDF生成成功 (HTTP $http_code)"
        log_info "処理時間: ${processing_time}秒"
        if [ -f "$OUTPUT_DIR/lifestyle-cover.pdf" ]; then
            file_size=$(stat -f%z "$OUTPUT_DIR/lifestyle-cover.pdf" 2>/dev/null || stat -c%s "$OUTPUT_DIR/lifestyle-cover.pdf" 2>/dev/null || echo "unknown")
            log_info "ファイルサイズ: ${file_size} bytes"
            log_info "出力ファイル: $OUTPUT_DIR/lifestyle-cover.pdf"
        fi
    else
        log_error "ライフスタイル誌表紙PDF生成失敗 (HTTP $http_code)"
        echo "$response"
    fi
}

# テック誌表紙テスト
test_tech_cover() {
    log_section "テック誌表紙テスト"
    log_info "POST /v2/pdf (tech-cover)"
    
    if [ ! -f "$SAMPLES_DIR/tech-cover-sample.json" ]; then
        log_error "サンプルファイルが見つかりません: $SAMPLES_DIR/tech-cover-sample.json"
        return 1
    fi
    
    start_time=$(date +%s.%N)
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X POST "$BASE_URL/v2/pdf" \
        -H "Content-Type: application/json" \
        --data @$SAMPLES_DIR/tech-cover-sample.json \
        --output "$OUTPUT_DIR/tech-cover.pdf")
    
    end_time=$(date +%s.%N)
    processing_time=$(echo "$end_time - $start_time" | bc)
    
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    
    if [ "$http_code" -eq 200 ]; then
        log_success "テック誌表紙PDF生成成功 (HTTP $http_code)"
        log_info "処理時間: ${processing_time}秒"
        if [ -f "$OUTPUT_DIR/tech-cover.pdf" ]; then
            file_size=$(stat -f%z "$OUTPUT_DIR/tech-cover.pdf" 2>/dev/null || stat -c%s "$OUTPUT_DIR/tech-cover.pdf" 2>/dev/null || echo "unknown")
            log_info "ファイルサイズ: ${file_size} bytes"
            log_info "出力ファイル: $OUTPUT_DIR/tech-cover.pdf"
        fi
    else
        log_error "テック誌表紙PDF生成失敗 (HTTP $http_code)"
        echo "$response"
    fi
}

# アート誌表紙テスト
test_art_cover() {
    log_section "アート誌表紙テスト"
    log_info "POST /v2/pdf (art-cover)"
    
    if [ ! -f "$SAMPLES_DIR/art-cover-sample.json" ]; then
        log_error "サンプルファイルが見つかりません: $SAMPLES_DIR/art-cover-sample.json"
        return 1
    fi
    
    start_time=$(date +%s.%N)
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X POST "$BASE_URL/v2/pdf" \
        -H "Content-Type: application/json" \
        --data @$SAMPLES_DIR/art-cover-sample.json \
        --output "$OUTPUT_DIR/art-cover.pdf")
    
    end_time=$(date +%s.%N)
    processing_time=$(echo "$end_time - $start_time" | bc)
    
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    
    if [ "$http_code" -eq 200 ]; then
        log_success "アート誌表紙PDF生成成功 (HTTP $http_code)"
        log_info "処理時間: ${processing_time}秒"
        if [ -f "$OUTPUT_DIR/art-cover.pdf" ]; then
            file_size=$(stat -f%z "$OUTPUT_DIR/art-cover.pdf" 2>/dev/null || stat -c%s "$OUTPUT_DIR/art-cover.pdf" 2>/dev/null || echo "unknown")
            log_info "ファイルサイズ: ${file_size} bytes"
            log_info "出力ファイル: $OUTPUT_DIR/art-cover.pdf"
        fi
    else
        log_error "アート誌表紙PDF生成失敗 (HTTP $http_code)"
        echo "$response"
    fi
}

# プレビューテスト
test_preview() {
    local template_name=$1
    log_section "${template_name} プレビューテスト"
    log_info "POST /v2/preview (${template_name})"
    
    if [ ! -f "$SAMPLES_DIR/${template_name}-sample.json" ]; then
        log_error "サンプルファイルが見つかりません: $SAMPLES_DIR/${template_name}-sample.json"
        return 1
    fi
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X POST "$BASE_URL/v2/preview" \
        -H "Content-Type: application/json" \
        --data @$SAMPLES_DIR/${template_name}-sample.json)
    
    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo $response | sed -e 's/HTTPSTATUS\:.*//g')
    
    if [ "$http_code" -eq 200 ]; then
        log_success "${template_name} プレビュー生成成功 (HTTP $http_code)"
        echo "$body" > "$OUTPUT_DIR/${template_name}-preview.html"
        log_info "プレビューファイル: $OUTPUT_DIR/${template_name}-preview.html"
        log_info "HTMLサイズ: $(echo "$body" | wc -c) bytes"
    else
        log_error "${template_name} プレビュー生成失敗 (HTTP $http_code)"
        echo "$body"
    fi
}

# 全テストの実行
test_all() {
    log_section "雑誌表紙テンプレート全テスト開始"
    
    # PDFテスト
    test_fashion_cover
    test_lifestyle_cover
    test_tech_cover
    test_art_cover
    
    # プレビューテスト
    test_preview "fashion-cover"
    test_preview "lifestyle-cover"
    test_preview "tech-cover"
    test_preview "art-cover"
    
    log_section "全テスト完了"
    log_info "出力ディレクトリ: $OUTPUT_DIR"
    log_info "生成されたファイル:"
    ls -la $OUTPUT_DIR/*.pdf $OUTPUT_DIR/*.html 2>/dev/null || log_warning "ファイルが見つかりません"
}

# メイン処理
case "${1:-all}" in
    "fashion-cover")
        test_fashion_cover
        test_preview "fashion-cover"
        ;;
    "lifestyle-cover")
        test_lifestyle_cover
        test_preview "lifestyle-cover"
        ;;
    "tech-cover")
        test_tech_cover
        test_preview "tech-cover"
        ;;
    "art-cover")
        test_art_cover
        test_preview "art-cover"
        ;;
    "all")
        test_all
        ;;
    *)
        echo "使用方法: $0 [template_name]"
        echo "テンプレート名: fashion-cover, lifestyle-cover, tech-cover, art-cover, all"
        exit 1
        ;;
esac 