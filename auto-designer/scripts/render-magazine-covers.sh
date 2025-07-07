#!/bin/bash

# 雑誌表紙テンプレート直接レンダリングスクリプト
# 使用方法: ./render-magazine-covers.sh [template_name]
# 例: ./render-magazine-covers.sh fashion-cover
# 例: ./render-magazine-covers.sh all

OUTPUT_DIR="./test-output"
SAMPLES_DIR="./samples"
TEMPLATES_DIR="./src/templates/magazine-covers"
NODE_SCRIPT="./scripts/render-template.js"

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
    console.error('使用方法: node render-template.js <template_path> <data_path> <output_path>');
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
    
    log_section "${template_name} テンプレートレンダリング"
    
    # ファイルパスを設定
    local template_file="$TEMPLATES_DIR/${template_name}.eta"
    local sample_file="$SAMPLES_DIR/${template_name}-sample.json"
    local html_output="$OUTPUT_DIR/${template_name}.html"
    local pdf_output="$OUTPUT_DIR/${template_name}.pdf"
    
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
        
        # ブラウザで開くかの確認
        echo ""
        echo "生成されたファイル:"
        echo "  HTML: $html_output"
        if [ -f "$pdf_output" ]; then
            echo "  PDF:  $pdf_output"
        fi
        echo ""
        read -p "HTMLファイルをブラウザで開きますか？ (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if command -v open >/dev/null 2>&1; then
                open "$html_output"
            elif command -v xdg-open >/dev/null 2>&1; then
                xdg-open "$html_output"
            else
                log_info "ブラウザを自動で開けません。手動で $html_output を開いてください。"
            fi
        fi
    else
        log_error "HTMLレンダリングに失敗しました"
        return 1
    fi
}

# 全テンプレートをレンダリング
render_all() {
    log_section "全雑誌表紙テンプレートレンダリング開始"
    
    # Node.jsレンダリングスクリプトを作成
    create_render_script
    
    local templates=("fashion-cover" "lifestyle-cover" "tech-cover" "art-cover")
    local success_count=0
    local total_count=${#templates[@]}
    
    for template in "${templates[@]}"; do
        render_template "$template"
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
        log_info "一時ファイルを削除しました"
    fi
}

# 依存関係チェック
check_dependencies() {
    log_info "依存関係をチェック中..."
    
    # Node.jsの確認
    if ! command -v node >/dev/null 2>&1; then
        log_error "Node.jsがインストールされていません"
        log_info "https://nodejs.org/ からNode.jsをインストールしてください"
        exit 1
    fi
    
    # etaパッケージの確認
    if ! node -e "require('eta')" 2>/dev/null; then
        log_error "etaパッケージがインストールされていません"
        log_info "以下のコマンドでインストールしてください:"
        log_info "npm install eta"
        exit 1
    fi
    
    log_success "依存関係チェック完了"
}

# メイン処理
main() {
    # 依存関係チェック
    check_dependencies
    
    case "${1:-all}" in
        "fashion-cover")
            render_template "fashion-cover"
            ;;
        "lifestyle-cover")
            render_template "lifestyle-cover"
            ;;
        "tech-cover")
            render_template "tech-cover"
            ;;
        "art-cover")
            render_template "art-cover"
            ;;
        "all")
            render_all
            ;;
        "help"|"-h"|"--help")
            echo "雑誌表紙テンプレート直接レンダリングスクリプト"
            echo ""
            echo "使用方法: $0 [template_name]"
            echo ""
            echo "テンプレート名:"
            echo "  fashion-cover   - ファッション誌風表紙"
            echo "  lifestyle-cover - ライフスタイル誌風表紙"
            echo "  tech-cover      - テック・ビジネス誌風表紙"
            echo "  art-cover       - アート・カルチャー誌風表紙"
            echo "  all             - 全テンプレート（デフォルト）"
            echo ""
            echo "オプション:"
            echo "  help, -h, --help - このヘルプを表示"
            echo ""
            echo "必要な依存関係:"
            echo "  - Node.js"
            echo "  - eta (npm install eta)"
            echo "  - pagedjs-cli (npm install -g pagedjs-cli) ※PDF生成用"
            ;;
        *)
            log_error "不明なテンプレート名: $1"
            echo ""
            echo "使用方法: $0 [template_name]"
            echo "利用可能なテンプレート: fashion-cover, lifestyle-cover, tech-cover, art-cover, all"
            echo "詳細なヘルプ: $0 help"
            exit 1
            ;;
    esac
}

# スクリプト実行
main "$@" 