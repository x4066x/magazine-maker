import os
import uuid
import json
from typing import Dict, List, Optional
from pathlib import Path
import mimetypes
from datetime import datetime

class FileService:
    """ファイル管理とメタデータ処理を担当するサービス"""
    
    def __init__(self, storage_path: str = "uploads"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # メタデータファイルのパス
        self.metadata_file = self.storage_path / "metadata.json"
        self.metadata = self._load_metadata()
        
        # サポートするファイルタイプとLINE Messaging APIのマッピング
        self.supported_types = {
            'image': ['image/jpeg', 'image/png', 'image/gif'],
            'video': ['video/mp4', 'video/quicktime'],
            'audio': ['audio/mpeg', 'audio/wav', 'audio/aac'],
            'file': ['application/pdf', 'application/zip', 'text/plain']
        }
    
    def _load_metadata(self) -> Dict:
        """メタデータファイルを読み込み"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f'Error loading metadata: {e}')
        return {}
    
    def _save_metadata(self):
        """メタデータファイルを保存"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f'Error saving metadata: {e}')
    
    def save_file(self, file_data: bytes, filename: str, content_type: Optional[str] = None) -> Dict:
        """ファイルを保存してメタデータを返す"""
        try:
            print(f"🔧 save_file開始: {filename}, サイズ: {len(file_data)} bytes")
            
            # ファイル名にUUIDを追加して重複を防ぐ
            file_id = str(uuid.uuid4())
            extension = Path(filename).suffix
            safe_filename = f"{file_id}{extension}"
            
            file_path = self.storage_path / safe_filename
            
            print(f"📁 保存パス: {file_path}")
            
            # ファイルを保存
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            print(f"✅ ファイル保存完了: {safe_filename}")
            
            # Content-Typeを推測
            if not content_type:
                content_type, _ = mimetypes.guess_type(filename)
            
            # メタデータを作成
            metadata = {
                'file_id': file_id,
                'original_filename': filename,
                'stored_filename': safe_filename,
                'file_path': str(file_path),
                'content_type': content_type,
                'file_size': len(file_data),
                'upload_time': datetime.now().isoformat(),
                'message_type': self.get_message_type(content_type)
            }
            
            print(f"📝 メタデータ作成: {file_id}")
            
            # メタデータを永続化
            self.metadata[file_id] = metadata
            self._save_metadata()
            
            print(f"💾 メタデータ保存完了: {len(self.metadata)} 件")
            print(f"📋 保存されたメタデータ: {metadata}")
            
            return metadata
            
        except Exception as e:
            print(f'❌ Error saving file: {e}')
            raise
    
    def get_message_type(self, content_type: str) -> str:
        """Content-TypeからLINE Messaging APIのメッセージタイプを判定"""
        if not content_type:
            return 'file'
        
        for msg_type, mime_types in self.supported_types.items():
            if content_type in mime_types:
                return msg_type
        
        return 'file'  # デフォルトはファイルメッセージ
    
    def get_file_url(self, file_id: str, base_url: str, message_type: str = 'file') -> str:
        """ファイルのURLを生成
        
        Args:
            file_id: ファイルID
            base_url: アプリケーションのベースURL
            message_type: メッセージタイプ（'image', 'video', 'audio', 'file'）
            
        Returns:
            str: ファイルにアクセスするためのURL
        """
        if message_type in ['image', 'video', 'audio']:
            return f"{base_url}/media/{message_type}/{file_id}"
        return f"{base_url}/files/{file_id}"
    
    def get_file_by_id(self, file_id: str) -> Optional[Dict]:
        """ファイルIDからファイル情報を取得"""
        try:
            print(f"🔍 get_file_by_id開始: {file_id}")
            print(f"📋 現在のメタデータ件数: {len(self.metadata)}")
            print(f"📋 メタデータのキー: {list(self.metadata.keys())}")
            
            # メタデータから検索
            if file_id in self.metadata:
                print(f"✅ メタデータからファイル発見: {file_id}")
                metadata = self.metadata[file_id]
                file_path_str = metadata['file_path']
                file_path = Path(file_path_str)
                
                # 相対パスの場合は絶対パスに変換
                if not file_path.is_absolute():
                    file_path = self.storage_path / file_path.name
                    print(f"📁 絶対パスに変換: {file_path}")
                
                # ファイルの存在確認
                if file_path.exists():
                    print(f"✅ ファイル存在確認: {file_path}")
                    # メタデータのファイルパスを絶対パスで更新
                    metadata['file_path'] = str(file_path)
                    return metadata
                else:
                    print(f"❌ ファイルが存在しません: {file_path}")
            else:
                print(f"❌ メタデータにファイルIDが見つかりません: {file_id}")
            
            # メタデータにない場合はファイルシステムから検索（フォールバック）
            print(f"🔍 ファイルシステムから検索開始: {file_id}")
            for file_path in self.storage_path.glob(f"{file_id}*"):
                print(f"📁 発見したファイル: {file_path}")
                if file_path.is_file():
                    content_type, _ = mimetypes.guess_type(str(file_path))
                    
                    # ファイルサイズを取得
                    file_size = file_path.stat().st_size
                    
                    # 元のファイル名を推測（拡張子から）
                    extension = file_path.suffix
                    original_filename = f"file{extension}"  # デフォルト名
                    
                    print(f"✅ フォールバックでファイル情報作成: {file_id}")
                    return {
                        'file_id': file_id,
                        'original_filename': original_filename,
                        'stored_filename': file_path.name,
                        'file_path': str(file_path),
                        'content_type': content_type,
                        'file_size': file_size,
                        'message_type': self.get_message_type(content_type)
                    }
            
            # 見つからない場合はNoneを返す
            print(f"❌ ファイルが見つかりません: {file_id}")
            return None
            
        except Exception as e:
            print(f'❌ Error getting file: {e}')
            import traceback
            print(f'❌ Traceback: {traceback.format_exc()}')
            return None
    
    def list_files(self) -> List[Dict]:
        """保存されているファイル一覧を取得"""
        files = []
        try:
            # メタデータから一覧を取得
            for file_id, metadata in self.metadata.items():
                file_path = Path(metadata['file_path'])
                if file_path.exists():
                    files.append(metadata)
            
            # メタデータにないファイルも検索（フォールバック）
            for file_path in self.storage_path.glob("*"):
                if file_path.is_file() and file_path.name != "metadata.json":
                    # 既にメタデータにあるファイルはスキップ
                    file_id = file_path.stem
                    if file_id not in self.metadata:
                        content_type, _ = mimetypes.guess_type(str(file_path))
                        files.append({
                            'file_id': file_id,
                            'filename': file_path.name,
                            'content_type': content_type,
                            'file_size': file_path.stat().st_size,
                            'message_type': self.get_message_type(content_type)
                        })
        except Exception as e:
            print(f'Error listing files: {e}')
        
        return files

# グローバルインスタンス
file_service = FileService() 