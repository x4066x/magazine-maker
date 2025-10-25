"""
メディアテンプレートのスキーマ定義

各メディアタイプ（自分史_縦書き、旅ログ_横書きなど）のページ構成と
必要なデータフィールドを定義します。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class PageType(Enum):
    """ページタイプの定義"""
    TITLE = "title"  # タイトルページ（カバー）
    SPREAD_FULL_IMAGE = "spread_full_image"  # 見開き画像フルページ
    SINGLE_IMAGE_TEXT = "single_image_text"  # 単一ページ画像+テキスト
    SPREAD_IMAGE_TEXT = "spread_image_text"  # 見開き画像+縦書きテキスト
    SINGLE_TEXT_ONLY = "single_text_only"  # テキストのみ（将来的に）


class WritingMode(Enum):
    """文字方向"""
    VERTICAL = "vertical"  # 縦書き
    HORIZONTAL = "horizontal"  # 横書き


@dataclass
class PageFieldSchema:
    """ページフィールドのスキーマ定義"""
    field_name: str  # フィールド名
    field_type: str  # "text" | "image" | "list"
    required: bool = True  # 必須かどうか
    default_value: Any = None  # デフォルト値
    description: str = ""  # フィールドの説明
    max_length: Optional[int] = None  # テキストの最大文字数
    placeholder: str = ""  # プレースホルダー


@dataclass
class PageSchema:
    """ページのスキーマ定義"""
    page_id: str  # ページID（例: "title_page", "spread_1", "single_1"）
    page_type: PageType  # ページタイプ
    page_number: int  # ページ番号（開始位置）
    display_name: str  # 表示名（ユーザー向け）
    description: str  # ページの説明
    fields: List[PageFieldSchema]  # このページに必要なフィールド
    template_path: str  # Vivliostyleテンプレートパス（modern/配下）
    is_deletable: bool = False  # ユーザーが削除可能か
    is_duplicatable: bool = False  # ユーザーが複製可能か


@dataclass
class MediaTemplateSchema:
    """メディアテンプレートのスキーマ定義"""
    template_id: str  # テンプレートID（例: "memoir_vertical"）
    template_name: str  # テンプレート名（例: "自分史_縦書き"）
    writing_mode: WritingMode  # 文字方向
    description: str  # テンプレートの説明
    pages: List[PageSchema]  # ページ構成
    category: str = "memoir"  # カテゴリ（memoir, travel, oshi, etc）
    
    def get_page_by_id(self, page_id: str) -> Optional[PageSchema]:
        """ページIDからページスキーマを取得"""
        for page in self.pages:
            if page.page_id == page_id:
                return page
        return None
    
    def get_required_images(self) -> List[Dict[str, str]]:
        """必要な画像フィールドのリストを取得（フロー用）"""
        images = []
        for page in self.pages:
            for field in page.fields:
                if field.field_type == "image" and field.required:
                    images.append({
                        "page_id": page.page_id,
                        "page_name": page.display_name,
                        "field_name": field.field_name,
                        "description": field.description
                    })
        return images


# ==========================================
# 自分史_縦書き テンプレート定義
# ==========================================

MEMOIR_VERTICAL_TEMPLATE = MediaTemplateSchema(
    template_id="memoir_vertical",
    template_name="自分史_縦書き",
    writing_mode=WritingMode.VERTICAL,
    description="縦書きの伝統的な自分史スタイル。タイトルページ、見開き画像ページ、単一画像+テキストページで構成されます。",
    category="memoir",
    pages=[
        # ページ1: タイトルページ（カバー）
        PageSchema(
            page_id="title_page",
            page_type=PageType.TITLE,
            page_number=1,
            display_name="表紙",
            description="自分史のタイトルと著者名を表示するカバーページ",
            template_path="title/modern-vertical-cover",
            fields=[
                PageFieldSchema(
                    field_name="title",
                    field_type="text",
                    required=True,
                    description="自分史のタイトル",
                    max_length=50,
                    placeholder="例：私の人生物語"
                ),
                PageFieldSchema(
                    field_name="author",
                    field_type="text",
                    required=True,
                    description="著者名",
                    max_length=30,
                    placeholder="例：鈴木太郎"
                ),
                PageFieldSchema(
                    field_name="cover_image",
                    field_type="image",
                    required=True,
                    description="カバー写真（縦長推奨）"
                ),
            ],
        ),
        
        # ページ2-3: 見開き画像+縦書きテキスト
        PageSchema(
            page_id="spread_1",
            page_type=PageType.SPREAD_IMAGE_TEXT,
            page_number=2,
            display_name="見開きページ（画像+縦書き）",
            description="左ページに大きな画像、右ページに縦書きのストーリー",
            template_path="spread/vertical-image-tategaki-spread",
            is_deletable=True,
            is_duplicatable=True,
            fields=[
                PageFieldSchema(
                    field_name="image",
                    field_type="image",
                    required=True,
                    description="見開きページ用の写真（縦長推奨）"
                ),
                PageFieldSchema(
                    field_name="story_title",
                    field_type="text",
                    required=False,
                    description="ストーリーのタイトル",
                    max_length=30,
                    placeholder="例：幼少期の思い出"
                ),
                PageFieldSchema(
                    field_name="story_text",
                    field_type="text",
                    required=True,
                    description="縦書きのストーリー本文",
                    max_length=2000,
                    placeholder="この時期の思い出やエピソードを書いてください"
                ),
            ],
        ),
        
        # ページ4: 単一ページ画像+テキスト
        PageSchema(
            page_id="single_1",
            page_type=PageType.SINGLE_IMAGE_TEXT,
            page_number=4,
            display_name="単一ページ（画像+テキスト）",
            description="1ページに画像とテキストを配置",
            template_path="single/vertical-central-image-single",
            is_deletable=True,
            is_duplicatable=True,
            fields=[
                PageFieldSchema(
                    field_name="image",
                    field_type="image",
                    required=True,
                    description="ページ用の写真"
                ),
                PageFieldSchema(
                    field_name="section_title",
                    field_type="text",
                    required=False,
                    description="セクションのタイトル",
                    max_length=30,
                    placeholder="例：学生時代"
                ),
                PageFieldSchema(
                    field_name="description",
                    field_type="text",
                    required=True,
                    description="画像の説明・ストーリー",
                    max_length=500,
                    placeholder="この写真について説明してください"
                ),
            ],
        ),
    ]
)


# ==========================================
# テンプレートレジストリ
# ==========================================

TEMPLATE_REGISTRY: Dict[str, MediaTemplateSchema] = {
    "memoir_vertical": MEMOIR_VERTICAL_TEMPLATE,
    # 将来的に追加:
    # "memoir_horizontal": MEMOIR_HORIZONTAL_TEMPLATE,
    # "travel_horizontal": TRAVEL_HORIZONTAL_TEMPLATE,
    # "oshi_vertical": OSHI_VERTICAL_TEMPLATE,
}


def get_template(template_id: str) -> Optional[MediaTemplateSchema]:
    """テンプレートIDからテンプレートスキーマを取得"""
    return TEMPLATE_REGISTRY.get(template_id)


def list_templates() -> List[Dict[str, str]]:
    """利用可能なテンプレートのリストを取得"""
    return [
        {
            "template_id": t.template_id,
            "template_name": t.template_name,
            "description": t.description,
            "category": t.category,
        }
        for t in TEMPLATE_REGISTRY.values()
    ]

