import os
from pathlib import Path
from typing import List

class Settings:
    """アプリケーション設定"""
    
    # プロジェクトルート
    PROJECT_ROOT = Path(__file__).parent.parent
    
    # テンプレートディレクトリ
    TEMPLATES_DIR = PROJECT_ROOT / "sample" / "templates"
    
    # サンプル画像ディレクトリ
    SAMPLE_IMAGES_DIR = PROJECT_ROOT / "sample" / "images"
    
    # 一時ファイルディレクトリ
    TEMP_DIR = PROJECT_ROOT / "temp"
    
    # 許可されたテンプレートID（ホワイトリスト）
    ALLOWED_TEMPLATE_IDS = [
        # タイトルページ
        "title/title-page",
        
        # 見開きページ
        "spread/quote-spread",
        "spread/text-image-spread", 
        "spread/balanced-spread",
        "spread/dual-image-spread",
        "spread/multi-image-spread",
        "spread/academic-spread",
        
        # 片面ページ
        "single/image-text-single",
        "single/text-wrap-image-single",
        "single/text-only-single",
        "single/minimal-single",
        "single/text-image-text-single",
        "single/text-focused-single",
        "single/summary-single"
    ]
    
    # Vivliostyle CLI設定
    VIVLIOSTYLE_TIMEOUT = int(os.getenv("VIVLIOSTYLE_TIMEOUT", "30"))
    VIVLIOSTYLE_OUTPUT_FORMAT = os.getenv("VIVLIOSTYLE_OUTPUT_FORMAT", "pdf")
    
    # セキュリティ設定
    MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE", "10485760"))  # 10MB
    ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
    
    # ログ設定
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def get_template_path(cls, template_id: str) -> Path:
        """テンプレートパスを取得"""
        return cls.TEMPLATES_DIR / template_id
    
    @classmethod
    def get_sample_image_path(cls, image_name: str) -> Path:
        """サンプル画像パスを取得"""
        return cls.SAMPLE_IMAGES_DIR / image_name
    
    @classmethod
    def is_allowed_template(cls, template_id: str) -> bool:
        """テンプレートIDが許可されているかチェック"""
        return template_id in cls.ALLOWED_TEMPLATE_IDS
    
    @classmethod
    def get_available_templates(cls) -> List[str]:
        """利用可能なテンプレート一覧を取得"""
        return cls.ALLOWED_TEMPLATE_IDS.copy()
    
    @classmethod
    def ensure_temp_dir(cls):
        """一時ディレクトリを作成"""
        cls.TEMP_DIR.mkdir(exist_ok=True)

# 設定インスタンス
settings = Settings() 