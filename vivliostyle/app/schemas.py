from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Payload(BaseModel):
    """PDF生成用のペイロード"""
    title: str = Field(..., description="タイトル")
    author: str = Field(..., description="著者名")
    images: List[str] = Field(default=[], description="画像パスのリスト")
    paragraphs: List[str] = Field(default=[], description="段落テキストのリスト")
    subtitle: Optional[str] = Field(None, description="サブタイトル")
    quote: Optional[str] = Field(None, description="引用文")
    quote_author: Optional[str] = Field(None, description="引用文の著者")
    additional_data: Optional[Dict[str, Any]] = Field(None, description="追加データ")

class GenerateRequest(BaseModel):
    """PDF生成リクエスト"""
    template_id: str = Field(..., description="テンプレートID")
    payload: Payload = Field(..., description="生成データ")

class GenerateResponse(BaseModel):
    """PDF生成レスポンス"""
    message: str = Field(..., description="レスポンスメッセージ")
    template_id: str = Field(..., description="使用したテンプレートID")
    file_size: Optional[int] = Field(None, description="生成されたPDFのファイルサイズ")

class TemplateInfo(BaseModel):
    """テンプレート情報"""
    id: str = Field(..., description="テンプレートID")
    name: str = Field(..., description="テンプレート名")
    description: str = Field(..., description="テンプレート説明")
    category: str = Field(..., description="カテゴリ（title/spread/single）")
    preview_image: Optional[str] = Field(None, description="プレビュー画像パス")

class HealthResponse(BaseModel):
    """ヘルスチェックレスポンス"""
    status: str = Field(..., description="システム状態")
    vivliostyle_cli: str = Field(..., description="Vivliostyle CLIの状態")
    vivliostyle_version: Optional[str] = Field(None, description="Vivliostyle CLIのバージョン")
    error: Optional[str] = Field(None, description="エラーメッセージ") 