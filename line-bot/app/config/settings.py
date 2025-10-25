"""アプリケーション設定"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()


class Settings:
    """アプリケーション設定クラス"""
    
    # LINE Bot 設定
    CHANNEL_ACCESS_TOKEN: str = os.environ.get('CHANNEL_ACCESS_TOKEN', 'your_channel_access_token')
    CHANNEL_SECRET: str = os.environ.get('CHANNEL_SECRET', 'your_channel_secret')
    
    # OpenAI 設定
    OPENAI_API_KEY: str = os.environ.get('OPENAI_API_KEY', 'your_openai_api_key')
    
    # アプリケーション設定
    BASE_URL: str = os.environ.get('BASE_URL', 'https://your-domain.com')
    
    # auto-designer API設定
    AUTO_DESIGNER_URL: str = os.environ.get('AUTO_DESIGNER_URL', 'http://localhost:3000')
    
    # ファイル保存設定
    UPLOADS_DIR: Path = Path("uploads")
    SAMPLES_DIR: Path = Path("samples")
    
    # サーバー設定
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    def __init__(self):
        # ディレクトリ作成
        self.UPLOADS_DIR.mkdir(exist_ok=True)
        self.SAMPLES_DIR.mkdir(exist_ok=True)
        
        # 環境変数の確認（セキュリティ上、最初の5文字のみ表示）
        print(f'CHANNEL_ACCESS_TOKEN: {self.CHANNEL_ACCESS_TOKEN[:5]}... (truncated for security)')
        print(f'CHANNEL_SECRET: {self.CHANNEL_SECRET[:5]}... (truncated for security)')
        print(f'OPENAI_API_KEY: {self.OPENAI_API_KEY[:5]}... (truncated for security)')


# グローバルインスタンス
settings = Settings()

