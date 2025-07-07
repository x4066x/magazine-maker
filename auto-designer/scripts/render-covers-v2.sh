#!/bin/bash

# 雑誌表紙テンプレート（covers-v2）レンダリングスクリプト
# 使用方法: ./render-covers-v2.sh [template_name]
# 例: ./render-covers-v2.sh cover-grid
# 例: ./render-covers-v2.sh all

OUTPUT_DIR="./test-output"
SAMPLES_DIR="./samples"
TEMPLATES_DIR="./src/templates/covers-v2"
NODE_SCRIPT="./scripts/render-template-v2.js"

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

# Node.jsレンダリングスクリプトを作成
create_render_script() {
    cat > $NODE_SCRIPT << 'EOF'
const { renderFile } = require('eta');
const fs = require('fs');
const path = require('path');

// コマンドライン引数を取得
const [,, templatePath, dataPath, outputPath] = process.argv;

if (!templatePath || !dataPath || !outputPath) {
    console.error('使用方法: node render-template-v2.js <template_path> <data_path> <output_path>');
    process.exit(1);
}

async function renderTemplate() {
    try {
        // データファイルを読み込み
        const dataContent = fs.readFileSync(dataPath, 'utf8');
        const data = JSON.parse(dataContent);
        
        // テンプレートファイルの絶対パスを取得
        const absoluteTemplatePath = path.resolve(templatePath);
        
        // テンプレートをレンダリング
        const html = await renderFile(absoluteTemplatePath, data.data || data);
        
        // HTMLファイルを出力
        fs.writeFileSync(outputPath, html, 'utf8');
        
        console.log(`✅ レンダリング成功: ${outputPath}`);
        console.log(`📄 HTMLサイズ: ${html.length} bytes`);
        
    } catch (error) {
        console.error('❌ レンダリングエラー:', error.message);
        process.exit(1);
    }
}

renderTemplate();
EOF
}

# PDFを生成する関数
generate_pdf() {
    local html_file=$1
    local pdf_file=$2
    
    log_info "HTMLからPDF生成中: $pdf_file"
    
    # pagedjs-cliを使用してPDFを生成
    if command -v pagedjs-cli >/dev/null 2>&1; then
        pagedjs-cli "$html_file" -o "$pdf_file" 2>/dev/null
        if [ $? -eq 0 ]; then
            log_success "PDF生成成功: $pdf_file"
            if [ -f "$pdf_file" ]; then
                file_size=$(stat -f%z "$pdf_file" 2>/dev/null || stat -c%s "$pdf_file" 2>/dev/null || echo "unknown")
                log_info "PDFサイズ: ${file_size} bytes"
            fi
        else
            log_warning "pagedjs-cliでのPDF生成に失敗しました"
        fi
    else
        log_warning "pagedjs-cliがインストールされていません。HTMLのみ生成します。"
        log_info "PDF生成には以下のコマンドでpagedjs-cliをインストールしてください:"
        log_info "npm install -g pagedjs-cli"
    fi
}

# テンプレートをレンダリングする関数
render_template() {
    local template_name=$1
    local sample_name=$2
    
    log_section "${template_name} テンプレートレンダリング (${sample_name})"
    
    # ファイルパスを設定
    local template_file="$TEMPLATES_DIR/${template_name}.eta"
    local sample_file="$SAMPLES_DIR/${sample_name}.json"
    local html_output="$OUTPUT_DIR/${template_name}_${sample_name}.html"
    local pdf_output="$OUTPUT_DIR/${template_name}_${sample_name}.pdf"
    
    # ファイルの存在確認
    if [ ! -f "$template_file" ]; then
        log_error "テンプレートファイルが見つかりません: $template_file"
        return 1
    fi
    
    if [ ! -f "$sample_file" ]; then
        log_error "サンプルデータファイルが見つかりません: $sample_file"
        return 1
    fi
    
    # Node.jsレンダリングスクリプトを作成（まだ存在しない場合）
    if [ ! -f "$NODE_SCRIPT" ]; then
        create_render_script
    fi
    
    # HTMLレンダリング
    log_info "HTMLレンダリング中..."
    node "$NODE_SCRIPT" "$template_file" "$sample_file" "$html_output"
    
    if [ $? -eq 0 ] && [ -f "$html_output" ]; then
        log_success "HTMLレンダリング成功: $html_output"
        
        # PDFを生成
        generate_pdf "$html_output" "$pdf_output"
        
        # 生成されたファイル情報を表示
        echo ""
        echo "生成されたファイル:"
        echo "  HTML: $html_output"
        if [ -f "$pdf_output" ]; then
            echo "  PDF:  $pdf_output"
        fi
        
        return 0
    else
        log_error "HTMLレンダリングに失敗しました"
        return 1
    fi
}

# 全テンプレートをレンダリング
render_all() {
    log_section "全covers-v2テンプレートレンダリング開始"
    
    # Node.jsレンダリングスクリプトを作成
    create_render_script
    
    # テンプレートとサンプルデータの組み合わせ
    local combinations=(
        "cover-grid:art-cover-sample"
        "cover-grid:tech-cover-sample"
        "cover-grid:lifestyle-cover-sample"
        "cover-grid:fashion-cover-sample"
        "cover-spilit:art-cover-sample"
        "cover-spilit:tech-cover-sample"
        "cover-spilit:lifestyle-cover-sample"
        "cover-spilit:fashion-cover-sample"
        "cover-overlay:art-cover-sample"
        "cover-overlay:tech-cover-sample"
        "cover-overlay:lifestyle-cover-sample"
        "cover-overlay:fashion-cover-sample"
    )
    
    local success_count=0
    local total_count=${#combinations[@]}
    
    for combination in "${combinations[@]}"; do
        IFS=':' read -r template_name sample_name <<< "$combination"
        render_template "$template_name" "$sample_name"
        if [ $? -eq 0 ]; then
            ((success_count++))
        fi
        echo ""
    done
    
    log_section "全テンプレートレンダリング完了"
    log_info "成功: $success_count/$total_count テンプレート"
    log_info "出力ディレクトリ: $OUTPUT_DIR"
    
    # 生成されたファイル一覧を表示
    echo ""
    echo "生成されたファイル:"
    ls -la $OUTPUT_DIR/*.html $OUTPUT_DIR/*.pdf 2>/dev/null || log_warning "ファイルが見つかりません"
    
    # クリーンアップ
    if [ -f "$NODE_SCRIPT" ]; then
        rm "$NODE_SCRIPT"
        log_info "一時ファイルを削除しました: $NODE_SCRIPT"
    fi
}

# メイン実行部分
case "$1" in
    "cover-grid")
        render_template "cover-grid" "art-cover-sample"
        ;;
    "cover-spilit")
        render_template "cover-spilit" "art-cover-sample"
        ;;
    "cover-overlay")
        render_template "cover-overlay" "art-cover-sample"
        ;;
    "all")
        render_all
        ;;
    *)
        echo "使用方法: $0 [cover-grid|cover-spilit|cover-overlay|all]"
        echo ""
        echo "例:"
        echo "  $0 cover-grid    # グリッドレイアウトテンプレート"
        echo "  $0 cover-spilit  # 分割レイアウトテンプレート"
        echo "  $0 cover-overlay # オーバーレイレイアウトテンプレート"
        echo "  $0 all          # 全テンプレート"
        exit 1
        ;;
esac 