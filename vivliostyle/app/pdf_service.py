import asyncio
import tempfile
import subprocess
import logging
import os
import shutil
from pathlib import Path
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader, Template
import time

from .settings import settings
from .schemas import Payload

logger = logging.getLogger(__name__)

class PDFService:
    """PDF生成サービス"""
    
    def __init__(self):
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(settings.TEMPLATES_DIR)),
            autoescape=True
        )
        settings.ensure_temp_dir()
    
    def get_available_templates(self) -> List[str]:
        """利用可能なテンプレート一覧を取得"""
        return settings.get_available_templates()
    
    async def generate_pdf(
        self, 
        template_id: str, 
        payload: Payload
    ) -> str:
        """PDFを生成"""
        
        # テンプレートIDの検証
        if not settings.is_allowed_template(template_id):
            raise ValueError(f"許可されていないテンプレートID: {template_id}")
        
        # 一時ディレクトリ作成
        with tempfile.TemporaryDirectory(dir=settings.TEMP_DIR) as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                # 1. テンプレートファイルをコピー
                template_path = settings.get_template_path(template_id)
                if not template_path.exists():
                    raise ValueError(f"テンプレートが見つかりません: {template_id}")
                
                # 2. 画像ファイルをコピー
                processed_images = await self._process_images(payload.images, temp_path)
                
                # 3. HTMLテンプレートを処理
                html_content = await self._render_template(
                    template_id, 
                    payload, 
                    processed_images
                )
                
                # 4. HTMLファイルを保存
                html_file = temp_path / "index.html"
                with open(html_file, "w", encoding="utf-8") as f:
                    f.write(html_content)
                
                # 5. Vivliostyle CLIでPDF生成
                pdf_path = await self._generate_pdf_with_vivliostyle(
                    html_file, 
                    temp_path
                )
                
                # 6. PDFファイルを一時ディレクトリにコピー（削除を遅延させるため）
                final_pdf_path = settings.TEMP_DIR / f"magazine_{int(time.time())}.pdf"
                shutil.copy2(pdf_path, final_pdf_path)
                
                logger.info(f"PDF生成完了: {final_pdf_path}")
                return str(final_pdf_path)
                
            except Exception as e:
                logger.error(f"PDF生成エラー: {str(e)}")
                raise
    
    async def _process_images(self, image_paths: List[str], temp_dir: Path) -> List[str]:
        """画像ファイルを処理して一時ディレクトリにコピーし、HTML用にはファイル名のみ返す"""
        processed_images = []
        
        for i, image_path in enumerate(image_paths):
            try:
                # サンプル画像パスの場合
                if not image_path.startswith(("http://", "https://", "/")):
                    sample_image_path = settings.get_sample_image_path(image_path)
                    if sample_image_path.exists():
                        # 一時ディレクトリにコピー
                        dest_path = temp_dir / f"image_{i}{sample_image_path.suffix}"
                        shutil.copy2(sample_image_path, dest_path)
                        processed_images.append(dest_path.name)  # ファイル名のみ
                        continue
                
                # 絶対パスの場合
                if os.path.exists(image_path):
                    dest_path = temp_dir / f"image_{i}{Path(image_path).suffix}"
                    shutil.copy2(image_path, dest_path)
                    processed_images.append(dest_path.name)  # ファイル名のみ
                else:
                    logger.warning(f"画像ファイルが見つかりません: {image_path}")
                    processed_images.append("")
                    
            except Exception as e:
                logger.error(f"画像処理エラー: {image_path}, {str(e)}")
                processed_images.append("")
        
        return processed_images
    
    async def _render_template(
        self, 
        template_id: str, 
        payload: Payload, 
        processed_images: List[str]
    ) -> str:
        """Jinja2テンプレートをレンダリング"""
        
        template_path = settings.get_template_path(template_id)
        html_file = template_path / "template.html"
        css_file = template_path / "style.css"
        
        if not html_file.exists():
            raise ValueError(f"HTMLテンプレートが見つかりません: {html_file}")
        
        # テンプレートを読み込み
        template = self.jinja_env.get_template(f"{template_id}/template.html")
        
        # CSSファイルの内容を読み込み
        css_content = ""
        if css_file.exists():
            with open(css_file, "r", encoding="utf-8") as f:
                css_content = f.read()
        
        # テンプレート変数を準備
        template_vars = {
            "title": payload.title,
            "author": payload.author,
            "images": processed_images,
            "paragraphs": payload.paragraphs,
            "subtitle": payload.subtitle,
            "quote": payload.quote,
            "quote_author": payload.quote_author,
            "css_content": css_content,
            "additional_data": payload.additional_data or {}
        }
        
        # テンプレートをレンダリング
        return template.render(**template_vars)
    
    async def _generate_pdf_with_vivliostyle(
        self, 
        html_file: Path, 
        output_dir: Path
    ) -> Path:
        """Vivliostyle CLIでPDFを生成"""
        
        output_file = output_dir / "output.pdf"
        
        # Vivliostyle CLIコマンド
        cmd = [
            "vivliostyle",
            "build",
            str(html_file),
            "--output", str(output_file),
            "--format", settings.VIVLIOSTYLE_OUTPUT_FORMAT,
            "--size", "A4",
            "--single-doc"
        ]
        
        logger.info(f"Vivliostyle CLI実行: {' '.join(cmd)}")
        
        try:
            # 非同期でコマンド実行
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=settings.VIVLIOSTYLE_TIMEOUT
            )
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise RuntimeError(f"Vivliostyle CLIエラー: {error_msg}")
            
            if not output_file.exists():
                raise RuntimeError("PDFファイルが生成されませんでした")
            
            logger.info(f"Vivliostyle CLI完了: {output_file}")
            return output_file
            
        except asyncio.TimeoutError:
            raise RuntimeError(f"Vivliostyle CLIがタイムアウトしました（{settings.VIVLIOSTYLE_TIMEOUT}秒）")
        except Exception as e:
            raise RuntimeError(f"Vivliostyle CLI実行エラー: {str(e)}") 