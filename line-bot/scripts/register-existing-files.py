#!/usr/bin/env python3
"""
既存のファイルをメタデータに登録するスクリプト
"""

import os
import sys
import json
import mimetypes
from pathlib import Path
from datetime import datetime

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from file_service import FileService

def register_existing_files():
    """既存のファイルをメタデータに登録"""
    
    # ファイルサービスを初期化
    file_service = FileService("uploads")
    
    # uploadsディレクトリのパス
    uploads_dir = Path("uploads")
    
    if not uploads_dir.exists():
        print("uploadsディレクトリが存在しません")
        return
    
    print("📁 既存ファイルの登録を開始...")
    
    # 各ファイルを処理
    for file_path in uploads_dir.glob("*"):
        if file_path.is_file() and file_path.name != "metadata.json":
            try:
                # ファイルIDを抽出（拡張子を除いた部分）
                file_id = file_path.stem
                
                # 既にメタデータに存在するかチェック
                if file_id in file_service.metadata:
                    print(f"✅ 既に登録済み: {file_path.name}")
                    continue
                
                # ファイル情報を取得
                content_type, _ = mimetypes.guess_type(str(file_path))
                file_size = file_path.stat().st_size
                
                # 元のファイル名を推測
                extension = file_path.suffix
                if extension == ".pdf":
                    original_filename = f"memoir_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                else:
                    original_filename = f"file{extension}"
                
                # メタデータを作成
                metadata = {
                    'file_id': file_id,
                    'original_filename': original_filename,
                    'stored_filename': file_path.name,
                    'file_path': str(file_path),
                    'content_type': content_type or 'application/octet-stream',
                    'file_size': file_size,
                    'upload_time': datetime.now().isoformat(),
                    'message_type': file_service.get_message_type(content_type or 'application/octet-stream')
                }
                
                # メタデータに追加
                file_service.metadata[file_id] = metadata
                
                print(f"📝 登録: {file_path.name} -> {original_filename}")
                
            except Exception as e:
                print(f"❌ エラー ({file_path.name}): {e}")
    
    # メタデータを保存
    file_service._save_metadata()
    
    print(f"\n✅ 登録完了！")
    print(f"📊 登録ファイル数: {len(file_service.metadata)}")
    
    # 登録されたファイル一覧を表示
    print("\n📋 登録されたファイル:")
    for file_id, metadata in file_service.metadata.items():
        print(f"  - {metadata['original_filename']} ({metadata['file_size']} bytes)")

if __name__ == "__main__":
    register_existing_files() 