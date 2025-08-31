#!/usr/bin/env python3
"""
モダンテンプレートのテストスクリプト
新しく作成したテンプレートが正しく表示されるかテストします
HTMLとPDFの両方をサポート
"""

import os
import webbrowser
import subprocess
import sys
from pathlib import Path

def test_templates():
    """作成したテンプレートをテストする"""
    
    # テンプレートのパス
    templates = {
        "モダンミニマル片面ページ": "sample/templates/modern/single/modern-minimal-single/index.html",
        "モダンバランス見開きページ": "sample/templates/modern/spread/modern-balanced-spread/index.html",
        "モダンタイトルページ": "sample/templates/modern/title/modern-title-page/index.html"
    }
    
    print("🎨 モダンテンプレートテスト")
    print("=" * 50)
    
    for name, path in templates.items():
        full_path = Path(path)
        if full_path.exists():
            print(f"✅ {name}: {path}")
            # ブラウザで開く
            try:
                webbrowser.open(f'file://{os.path.abspath(full_path)}')
                print(f"   📖 ブラウザで開きました")
            except Exception as e:
                print(f"   ❌ ブラウザで開けませんでした: {e}")
        else:
            print(f"❌ {name}: {path} (ファイルが見つかりません)")
    
    print("\n📝 使用方法:")
    print("1. ブラウザでテンプレートが開かれます")
    print("2. デザインを確認し、必要に応じてCSSを調整")
    print("3. 印刷プレビューでPDF出力の確認も可能")
    
    print("\n🔧 CSS調整のポイント:")
    print("- 色やフォントサイズの変更")
    print("- レイアウトの微調整")
    print("- 装飾要素の追加・削除")
    print("- 印刷時の最適化")

def build_pdfs():
    """PDFをビルドする"""
    print("\n🔄 PDFビルドを開始します...")
    
    # 出力ディレクトリの作成
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # 個別テンプレートのPDFビルド
    templates = {
        "タイトルページ": "sample/templates/modern/title/modern-title-page/index.html",
        "片面ページ": "sample/templates/modern/single/modern-minimal-single/index.html",
        "見開きページ": "sample/templates/modern/spread/modern-balanced-spread/index.html"
    }
    
    for name, path in templates.items():
        print(f"  📄 {name}のPDFを生成中...")
        output_file = output_dir / f"{name.lower().replace('ページ', '')}.pdf"
        
        try:
            # vivliostyle buildコマンドを実行
            cmd = ["vivliostyle", "build", path, "-o", str(output_file)]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
            
            if result.returncode == 0:
                print(f"    ✅ {output_file.name} が生成されました")
            else:
                print(f"    ❌ エラー: {result.stderr}")
        except FileNotFoundError:
            print(f"    ❌ vivliostyleコマンドが見つかりません")
            print("    💡 インストール方法: npm install -g @vivliostyle/cli")
            return False
        except Exception as e:
            print(f"    ❌ 予期しないエラー: {e}")
            return False
    
    # 統合PDFのビルド
    print("  📚 統合PDFを生成中...")
    try:
        cmd = ["vivliostyle", "build", "vivliostyle.config.js"]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode == 0:
            print("    ✅ 統合PDFが生成されました")
        else:
            print(f"    ❌ エラー: {result.stderr}")
    except Exception as e:
        print(f"    ❌ 統合PDFの生成でエラー: {e}")
    
    print(f"\n📁 出力ファイル:")
    for pdf_file in output_dir.glob("*.pdf"):
        print(f"  - {pdf_file.name}")
    
    return True

def show_template_structure():
    """テンプレート構造を表示"""
    
    print("\n📁 テンプレート構造:")
    print("=" * 50)
    
    structure = """
vivliostyle/
├── sample/
│   ├── templates/
│   │   └── modern/
│   │       ├── single/
│   │       │   └── modern-minimal-single/
│   │       │       ├── index.html
│   │       │       └── style.css
│   │       ├── spread/
│   │       │   └── modern-balanced-spread/
│   │       │       ├── index.html
│   │       │       └── style.css
│   │       └── title/
│   │           └── modern-title-page/
│   │               ├── index.html
│   │               └── style.css
│   └── images/
│       ├── 1_1080x1920.jpg
│       ├── 3_1080x1920.jpg
│       ├── 6_1080x1080.jpg
│       └── ...
├── vivliostyle.config.js
├── build-pdf.sh
└── output/
    ├── title-page.pdf
    ├── single-page.pdf
    ├── spread-page.pdf
    └── modern-templates.pdf
"""
    
    print(structure)

def main():
    """メイン関数"""
    print("🎨 モダンテンプレート管理ツール")
    print("=" * 50)
    
    while True:
        print("\n選択してください:")
        print("1. HTMLテンプレートをテスト")
        print("2. PDFをビルド")
        print("3. テンプレート構造を表示")
        print("4. 終了")
        
        choice = input("\n選択 (1-4): ").strip()
        
        if choice == "1":
            test_templates()
        elif choice == "2":
            build_pdfs()
        elif choice == "3":
            show_template_structure()
        elif choice == "4":
            print("👋 終了します")
            break
        else:
            print("❌ 無効な選択です。1-4の数字を入力してください。")

if __name__ == "__main__":
    main()
