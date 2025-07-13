#!/usr/bin/env python3
"""
サンプル画像生成スクリプト
雑誌風PDF生成のテスト用に適切なサイズと内容の画像を生成します
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_sample_image(filename, size, index):
    """サンプル画像を作成"""
    # スマホ用サイズで画像作成
    img = Image.new('RGB', size, color=(240, 240, 240))  # 薄いグレー背景
    draw = ImageDraw.Draw(img)
    
    # 淡い色のパレット（加工時に分かりやすい色）
    pastel_colors = [
        (255, 182, 193),  # 薄いピンク
        (173, 216, 230),  # 薄い青
        (144, 238, 144),  # 薄い緑
        (255, 218, 185),  # 薄いオレンジ
        (221, 160, 221),  # 薄い紫
        (255, 255, 224),  # 薄い黄色
        (240, 248, 255),  # 薄い水色
        (255, 228, 225),  # 薄いサーモン
        (245, 245, 220),  # ベージュ
    ]
    
    # マス目のサイズ（画像サイズに応じて調整）
    grid_size = min(size) // 8
    
    # マス目を描画
    for x in range(0, size[0], grid_size):
        for y in range(0, size[1], grid_size):
            # マス目の色を順番に設定
            color_index = ((x // grid_size) + (y // grid_size)) % len(pastel_colors)
            color = pastel_colors[color_index]
            
            # マス目を描画
            draw.rectangle([x, y, x + grid_size, y + grid_size], fill=color, outline=(200, 200, 200), width=1)
    
    # 加工時に分かりやすい要素を追加
    # 中央に大きな円を描画
    center_x, center_y = size[0] // 2, size[1] // 2
    circle_radius = min(size) // 4  # 円を大きくする
    draw.ellipse([center_x - circle_radius, center_y - circle_radius, 
                  center_x + circle_radius, center_y + circle_radius], 
                 fill=(255, 255, 255), outline=(100, 100, 100), width=3)
    
    # フォント設定（大きな番号用）
    try:
        # macOS用フォント
        font_size = min(size) // 12  # フォントサイズをさらに小さく調整
        font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', font_size)
    except:
        try:
            # 代替フォント
            font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', font_size)
        except:
            # デフォルトフォント
            font = ImageFont.load_default()
    
    # 表示テキスト（番号とサイズ）
    text = f"{index}\n{size[0]}x{size[1]}"
    
    # テキスト位置を中央に配置
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = center_x - text_width // 2
    y = center_y - text_height // 2
    
    # テキスト描画（黒文字）
    draw.text((x, y), text, fill='black', font=font)
    
    # 加工時に分かりやすい要素を追加
    # 四隅に小さなマーカーを描画
    marker_size = min(size) // 20
    marker_color = (255, 0, 0)  # 赤色
    
    # 左上
    draw.rectangle([5, 5, 5 + marker_size, 5 + marker_size], fill=marker_color)
    # 右上
    draw.rectangle([size[0] - 5 - marker_size, 5, size[0] - 5, 5 + marker_size], fill=marker_color)
    # 左下
    draw.rectangle([5, size[1] - 5 - marker_size, 5 + marker_size, size[1] - 5], fill=marker_color)
    # 右下
    draw.rectangle([size[0] - 5 - marker_size, size[1] - 5 - marker_size, size[0] - 5, size[1] - 5], fill=marker_color)
    
    # ファイル保存
    if filename.endswith('.png'):
        img.save(filename, 'PNG')
    else:
        img.save(filename, 'JPEG', quality=95)
    
    print(f"作成完了: {filename} ({size[0]}x{size[1]}) - #{index}")

def main():
    """メイン処理"""
    print("サンプル画像を生成しています...")
    
    # スマホ用画像設定（縦長、横長、正方形）
    images_config = [
        # (サイズ, 拡張子)
        ((1080, 1920), 'jpg'),  # 1
        ((1080, 1920), 'jpg'),  # 2
        ((1080, 1920), 'jpg'),  # 3
        ((1920, 1080), 'jpg'),  # 4
        ((1920, 1080), 'jpg'),  # 5
        ((1080, 1080), 'jpg'),  # 6
        ((1080, 1080), 'jpg'),  # 7
        ((1080, 1920), 'jpg'),  # 8
        ((512, 512),   'png'),  # 9
    ]
    
    # 画像生成
    for idx, (size, ext) in enumerate(images_config, 1):
        filename = f"{idx}_{size[0]}x{size[1]}.{ext}"
        create_sample_image(filename, size, idx)
    
    print("\nすべてのサンプル画像の生成が完了しました！")
    print("生成された画像:")
    for idx, (size, ext) in enumerate(images_config, 1):
        filename = f"{idx}_{size[0]}x{size[1]}.{ext}"
        print(f"  - {filename}")

if __name__ == "__main__":
    main() 