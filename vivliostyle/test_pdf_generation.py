#!/usr/bin/env python3
"""
PDF生成テストスクリプト
サンプル画像を使用して各テンプレートでPDFを生成します
"""

import asyncio
import json
import sys
import argparse
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.pdf_service import PDFService
from app.schemas import Payload

def split_text_by_length(text, max_length=300):
    """指定文字数ごとにテキストを分割しリストで返す"""
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

# 利用可能な画像一覧
AVAILABLE_IMAGES = {
    "縦長（ポートレート）": [
        "1_1080x1920.jpg",
        "2_1080x1920.jpg", 
        "3_1080x1920.jpg",
        "8_1080x1920.jpg"
    ],
    "横長（ランドスケープ）": [
        "4_1920x1080.jpg",
        "5_1920x1080.jpg"
    ],
    "正方形": [
        "6_1080x1080.jpg",
        "7_1080x1080.jpg",
        "9_512x512.png"
    ]
}

# テストケース定義
TEST_CASES = {
    "title/title-page": {
        "name": "タイトルページ",
        "payload": Payload(
            title="旅の思い出",
            author="山田太郎",
            subtitle="美しい風景との出会い",
            images=["1_1080x1920.jpg"],
            paragraphs=[]
        )
    },
    "spread/quote-spread": {
        "name": "引用文見開きページ",
        "payload": Payload(
            title="人生の名言",
            author="名言集",
            quote="人生は美しい。それは美しい心で見るからだ。",
            quote_author="アンリ・マティス",
            images=["2_1080x1920.jpg"],
            paragraphs=[]
        )
    },
    "single/image-text-single": {
        "name": "画像+テキスト片面ページ",
        "payload": Payload(
            title="美しい風景",
            author="写真家 田中花子",
            images=["3_1080x1920.jpg"],
            paragraphs=[
                "この風景を見た瞬間、心が洗われるような感覚を覚えました。",
                "自然の美しさは、私たちに多くのことを教えてくれます。",
                "忙しい日常の中でも、時には立ち止まって周りを見回してみることで、新しい発見があるかもしれません。"
            ]
        )
    },
    "single/text-wrap-image-single": {
        "name": "テキスト周り込み画像片面ページ",
        "payload": Payload(
            title="自然との対話",
            author="自然作家 佐藤美咲",
            images=["4_1920x1080.jpg", "5_1920x1080.jpg"],
            paragraphs=split_text_by_length(
                "森の中を歩いていると、木々のざわめきが心に響いてきます。風が葉を揺らす音、小鳥のさえずり、そして遠くから聞こえる川のせせらぎ。これらの自然の音は、私たちに何かを語りかけているようです。現代社会では、人工的な音に囲まれて生活することが多いですが、時には自然の中に身を置いて、心をリセットすることも大切です。自然は私たちの心の奥深くにある何かを呼び覚ましてくれます。さらに、季節ごとに変化する森の表情や、朝露に濡れた葉のきらめき、夕暮れ時の静けさなど、自然の中には日常では味わえない特別な瞬間がたくさんあります。私たちは忙しい毎日の中で、つい自然の存在を忘れがちですが、ふと立ち止まって耳を澄ませば、そこには豊かな命の営みが広がっています。自然と向き合うことで、自分自身の心とも静かに対話できるのです。",
                max_length=300
            )
        )
    }
}

def show_available_images():
    """利用可能な画像一覧を表示"""
    print("=" * 60)
    print("利用可能な画像一覧:")
    print("=" * 60)
    
    for category, images in AVAILABLE_IMAGES.items():
        print(f"\n{category}:")
        for i, image in enumerate(images, 1):
            print(f"  {i}. {image}")
    
    print("\n" + "=" * 60)

def show_available_templates():
    """利用可能なテンプレート一覧を表示"""
    print("=" * 60)
    print("利用可能なテンプレート一覧:")
    print("=" * 60)
    
    for i, (template_id, info) in enumerate(TEST_CASES.items(), 1):
        print(f"{i}. {info['name']} ({template_id})")
    
    print("\n" + "=" * 60)

async def test_pdf_generation(selected_pages=None):
    """PDF生成をテスト"""
    
    # PDFサービスインスタンス作成
    pdf_service = PDFService()
    
    # 選択されたページのみフィルタリング
    if selected_pages:
        test_cases = []
        for page_num in selected_pages:
            if 1 <= page_num <= len(TEST_CASES):
                template_id = list(TEST_CASES.keys())[page_num - 1]
                test_cases.append({
                    "template_id": template_id,
                    "name": TEST_CASES[template_id]["name"],
                    "payload": TEST_CASES[template_id]["payload"]
                })
    else:
        # 全ページ生成
        test_cases = [
            {
                "template_id": template_id,
                "name": info["name"],
                "payload": info["payload"]
            }
            for template_id, info in TEST_CASES.items()
        ]
    
    print("PDF生成テストを開始します...")
    print(f"利用可能なテンプレート: {pdf_service.get_available_templates()}")
    print(f"生成対象: {len(test_cases)}ページ")
    print("-" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            print(f"{i}. {test_case['name']} ({test_case['template_id']}) を生成中...")
            
            # PDF生成
            pdf_path = await pdf_service.generate_pdf(
                template_id=test_case['template_id'],
                payload=test_case['payload']
            )
            
            print(f"   ✓ 生成完了: {pdf_path}")
            
        except Exception as e:
            print(f"   ✗ エラー: {str(e)}")
    
    print("-" * 50)
    print("テスト完了")

def test_curl_command():
    """curlコマンドの例を表示"""
    
    print("\n" + "="*60)
    print("curlコマンドでのテスト例:")
    print("="*60)
    
    curl_examples = [
        {
            "name": "タイトルページ",
            "template": "title/title-page",
            "command": '''curl -X POST http://localhost:8000/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "template_id": "title/title-page",
    "payload": {
      "title": "旅の思い出",
      "author": "山田太郎",
      "subtitle": "美しい風景との出会い",
      "images": ["1_1080x1920.jpg"],
      "paragraphs": []
    }
  }' --output title_page.pdf'''
        },
        {
            "name": "引用文見開きページ",
            "template": "spread/quote-spread",
            "command": '''curl -X POST http://localhost:8000/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "template_id": "spread/quote-spread",
    "payload": {
      "title": "人生の名言",
      "author": "名言集",
      "quote": "人生は美しい。それは美しい心で見るからだ。",
      "quote_author": "アンリ・マティス",
      "images": ["2_1080x1920.jpg"],
      "paragraphs": []
    }
  }' --output quote_spread.pdf'''
        },
        {
            "name": "画像+テキスト片面ページ",
            "template": "single/image-text-single",
            "command": '''curl -X POST http://localhost:8000/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "template_id": "single/image-text-single",
    "payload": {
      "title": "美しい風景",
      "author": "写真家 田中花子",
      "images": ["3_1080x1920.jpg"],
      "paragraphs": [
        "この風景を見た瞬間、心が洗われるような感覚を覚えました。",
        "自然の美しさは、私たちに多くのことを教えてくれます。",
        "忙しい日常の中でも、時には立ち止まって周りを見回してみることで、新しい発見があるかもしれません。"
      ]
    }
  }' --output image_text_single.pdf'''
        },
        {
            "name": "テキスト周り込み画像片面ページ",
            "template": "single/text-wrap-image-single",
            "command": '''curl -X POST http://localhost:8000/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "template_id": "single/text-wrap-image-single",
    "payload": {
      "title": "自然との対話",
      "author": "自然作家 佐藤美咲",
      "images": ["4_1920x1080.jpg", "5_1920x1080.jpg"],
      "paragraphs": [
        "森の中を歩いていると、木々のざわめきが心に響いてきます。風が葉を揺らす音、小鳥のさえずり、そして遠くから聞こえる川のせせらぎ。これらの自然の音は、私たちに何かを語りかけているようです。現代社会では、人工的な音に囲まれて生活することが多いですが、時には自然の中に身を置いて、心をリセットすることも大切です。自然は私たちの心の奥深くにある何かを呼び覚ましてくれます。さらに、季節ごとに変化する森の表情や、朝露に濡れた葉のきらめき、夕暮れ時の静けさなど、自然の中には日常では味わえない特別な瞬間がたくさんあります。私たちは忙しい毎日の中で、つい自然の存在を忘れがちですが、ふと立ち止まって耳を澄ませば、そこには豊かな命の営みが広がっています。自然と向き合うことで、自分自身の心とも静かに対話できるのです。"
      ]
    }
  }' --output text_wrap_image_single.pdf'''
        }
    ]
    
    for example in curl_examples:
        print(f"\n{example['name']} ({example['template']}):")
        print(example['command'])
        print()

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='PDF生成テストスクリプト')
    parser.add_argument('--pages', '-p', nargs='+', type=int, 
                       help='生成するページ番号（1-4）。例: --pages 1 3 4')
    parser.add_argument('--images', '-i', action='store_true',
                       help='利用可能な画像一覧を表示')
    parser.add_argument('--templates', '-t', action='store_true',
                       help='利用可能なテンプレート一覧を表示')
    parser.add_argument('--curl', '-c', action='store_true',
                       help='curlコマンド例を表示')
    
    args = parser.parse_args()
    
    # 画像一覧表示
    if args.images:
        show_available_images()
        return
    
    # テンプレート一覧表示
    if args.templates:
        show_available_templates()
        return
    
    # curl例表示
    if args.curl:
        test_curl_command()
        return
    
    # ページ番号の検証
    if args.pages:
        for page_num in args.pages:
            if page_num < 1 or page_num > len(TEST_CASES):
                print(f"エラー: ページ番号 {page_num} は無効です。有効な範囲: 1-{len(TEST_CASES)}")
                return
    
    # 非同期テスト実行
    asyncio.run(test_pdf_generation(args.pages))

if __name__ == "__main__":
    main() 