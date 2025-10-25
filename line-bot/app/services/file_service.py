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
    
    def _get_owner_directory(self, owner_type: str, owner_id: str) -> Path:
        """所有者のディレクトリパスを取得
        
        Args:
            owner_type: "user" または "group"
            owner_id: ユーザーIDまたはグループID
        
        Returns:
            所有者のディレクトリパス
        """
        dir_name = f"{owner_type}_{owner_id}"
        owner_dir = self.storage_path / dir_name
        owner_dir.mkdir(exist_ok=True)
        return owner_dir
    
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
    
    def save_file(
        self, 
        file_data: bytes, 
        filename: str, 
        content_type: Optional[str] = None,
        owner_type: str = "user",
        owner_id: Optional[str] = None,
        uploader_id: Optional[str] = None
    ) -> Dict:
        """ファイルを保存してメタデータを返す
        
        Args:
            file_data: ファイルデータ
            filename: ファイル名
            content_type: Content-Type
            owner_type: 所有者タイプ ("user" または "group")
            owner_id: 所有者ID (user_id または group_id)
            uploader_id: アップロードしたユーザーID
        
        Returns:
            ファイルメタデータ
        """
        try:
            print(f"🔧 save_file開始: {filename}, サイズ: {len(file_data)} bytes")
            print(f"👤 owner_type={owner_type}, owner_id={owner_id}, uploader_id={uploader_id}")
            
            # owner_idがない場合は後方互換性のため、uploadsディレクトリに保存
            if owner_id:
                owner_dir = self._get_owner_directory(owner_type, owner_id)
            else:
                owner_dir = self.storage_path
                print(f"⚠️ owner_id未指定のため、ルートディレクトリに保存")
            
            # ファイル名にUUIDを追加して重複を防ぐ
            file_id = str(uuid.uuid4())
            extension = Path(filename).suffix
            safe_filename = f"{file_id}{extension}"
            
            file_path = owner_dir / safe_filename
            
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
                'message_type': self.get_message_type(content_type),
                'owner_type': owner_type,
                'owner_id': owner_id,
                'uploader_id': uploader_id or owner_id  # uploader_idがない場合はowner_idを使用
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
    
    def get_file_url(
        self, 
        file_id: str, 
        base_url: str, 
        message_type: str = 'file',
        requester_user_id: Optional[str] = None,
        requester_group_id: Optional[str] = None
    ) -> str:
        """ファイルのURLを生成
        
        Args:
            file_id: ファイルID
            base_url: アプリケーションのベースURL
            message_type: メッセージタイプ（'image', 'video', 'audio', 'file'）
            requester_user_id: リクエストユーザーID（認証用）
            requester_group_id: リクエストグループID（認証用）
            
        Returns:
            str: ファイルにアクセスするためのURL（認証パラメータ付き）
        """
        # ベースURL生成
        if message_type in ['image', 'video', 'audio']:
            url = f"{base_url}/media/{message_type}/{file_id}"
        else:
            url = f"{base_url}/files/{file_id}"
        
        # 認証パラメータを追加
        params = []
        if requester_user_id:
            params.append(f"user_id={requester_user_id}")
        if requester_group_id:
            params.append(f"group_id={requester_group_id}")
        
        if params:
            url += "?" + "&".join(params)
        
        return url
    
    def get_file_by_id(
        self, 
        file_id: str, 
        requester_user_id: Optional[str] = None,
        requester_group_id: Optional[str] = None
    ) -> Optional[Dict]:
        """ファイルIDからファイル情報を取得
        
        Args:
            file_id: ファイルID
            requester_user_id: リクエストしたユーザーID（アクセス制御用）
            requester_group_id: リクエストしたグループID（アクセス制御用）
        
        Returns:
            ファイルメタデータ（アクセス権がある場合）
        """
        try:
            print(f"🔍 get_file_by_id開始: {file_id}")
            print(f"👤 requester_user_id={requester_user_id}, requester_group_id={requester_group_id}")
            print(f"📋 現在のメタデータ件数: {len(self.metadata)}")
            
            # メタデータから検索
            if file_id in self.metadata:
                print(f"✅ メタデータからファイル発見: {file_id}")
                metadata = self.metadata[file_id]
                
                # アクセス制御チェック
                if requester_user_id or requester_group_id:
                    if not self._check_access(metadata, requester_user_id, requester_group_id):
                        print(f"❌ アクセス権限がありません: {file_id}")
                        return None
                    print(f"✅ アクセス権限確認OK")
                
                file_path_str = metadata['file_path']
                file_path = Path(file_path_str)
                
                # 相対パスの場合は絶対パスに変換
                if not file_path.is_absolute():
                    # owner_idがある場合は、owner_directory配下を探す
                    if 'owner_id' in metadata and 'owner_type' in metadata:
                        owner_dir = self._get_owner_directory(metadata['owner_type'], metadata['owner_id'])
                        file_path = owner_dir / file_path.name
                    else:
                        # 後方互換性: ルートディレクトリ
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
            
            # メタデータにない場合はファイルシステムから検索（フォールバック・後方互換性）
            print(f"🔍 ファイルシステムから検索開始（後方互換性）: {file_id}")
            
            # ルートディレクトリを検索
            for file_path in self.storage_path.glob(f"{file_id}*"):
                if file_path.is_file():
                    print(f"📁 発見したファイル: {file_path}")
                    content_type, _ = mimetypes.guess_type(str(file_path))
                    file_size = file_path.stat().st_size
                    extension = file_path.suffix
                    original_filename = f"file{extension}"
                    
                    print(f"✅ フォールバックでファイル情報作成: {file_id}")
                    return {
                        'file_id': file_id,
                        'original_filename': original_filename,
                        'stored_filename': file_path.name,
                        'file_path': str(file_path),
                        'content_type': content_type,
                        'file_size': file_size,
                        'message_type': self.get_message_type(content_type)
                        # 後方互換性のためowner情報なし
                    }
            
            # 見つからない場合はNoneを返す
            print(f"❌ ファイルが見つかりません: {file_id}")
            return None
            
        except Exception as e:
            print(f'❌ Error getting file: {e}')
            import traceback
            print(f'❌ Traceback: {traceback.format_exc()}')
            return None
    
    def _check_access(
        self, 
        metadata: Dict, 
        requester_user_id: Optional[str],
        requester_group_id: Optional[str]
    ) -> bool:
        """ファイルへのアクセス権限をチェック
        
        Args:
            metadata: ファイルメタデータ
            requester_user_id: リクエストしたユーザーID
            requester_group_id: リクエストしたグループID
        
        Returns:
            アクセス可能ならTrue
        """
        # owner情報がない場合は後方互換性のため許可
        if 'owner_type' not in metadata or 'owner_id' not in metadata:
            print(f"⚠️ owner情報なし（後方互換性）: アクセス許可")
            return True
        
        owner_type = metadata['owner_type']
        owner_id = metadata['owner_id']
        
        # ユーザー所有のファイル
        if owner_type == "user":
            # リクエストしたユーザーが所有者と一致するか
            if requester_user_id == owner_id:
                print(f"✅ ユーザー所有ファイル: 所有者アクセス")
                return True
        
        # グループ所有のファイル
        elif owner_type == "group":
            # リクエストしたグループIDが一致するか
            if requester_group_id == owner_id:
                print(f"✅ グループ所有ファイル: グループメンバーアクセス")
                return True
        
        print(f"❌ アクセス権限なし: owner={owner_type}:{owner_id}, requester=user:{requester_user_id}/group:{requester_group_id}")
        return False
    
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

