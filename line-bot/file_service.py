import os
import uuid
from typing import Dict, List, Optional
from pathlib import Path
import mimetypes
from datetime import datetime

class FileService:
    """ファイル管理とメタデータ処理を担当するサービス"""
    
    def __init__(self, storage_path: str = "uploads"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # サポートするファイルタイプとLINE Messaging APIのマッピング
        self.supported_types = {
            'image': ['image/jpeg', 'image/png', 'image/gif'],
            'video': ['video/mp4', 'video/quicktime'],
            'audio': ['audio/mpeg', 'audio/wav', 'audio/aac'],
            'file': ['application/pdf', 'application/zip', 'text/plain']
        }
    
    def save_file(self, file_data: bytes, filename: str, content_type: Optional[str] = None) -> Dict:
        """ファイルを保存してメタデータを返す"""
        try:
            # ファイル名にUUIDを追加して重複を防ぐ
            file_id = str(uuid.uuid4())
            extension = Path(filename).suffix
            safe_filename = f"{file_id}{extension}"
            
            file_path = self.storage_path / safe_filename
            
            # ファイルを保存
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
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
            
            return metadata
            
        except Exception as e:
            print(f'Error saving file: {e}')
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
            # 実際の実装では、データベースやメタデータファイルから情報を取得
            # ここでは簡単な実装として、ファイルシステムから検索
            for file_path in self.storage_path.glob(f"{file_id}*"):
                if file_path.is_file():
                    content_type, _ = mimetypes.guess_type(str(file_path))
                    return {
                        'file_id': file_id,
                        'file_path': str(file_path),
                        'content_type': content_type,
                        'file_size': file_path.stat().st_size
                    }
            return None
        except Exception as e:
            print(f'Error getting file: {e}')
            return None
    
    def list_files(self) -> List[Dict]:
        """保存されているファイル一覧を取得"""
        files = []
        try:
            for file_path in self.storage_path.glob("*"):
                if file_path.is_file():
                    content_type, _ = mimetypes.guess_type(str(file_path))
                    file_id = file_path.stem
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