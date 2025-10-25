"""
Vivliostyle PDF生成サービス
"""

import asyncio
import tempfile
import shutil
import logging
import requests
from pathlib import Path
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader


logger = logging.getLogger(__name__)


class VivliostyleService:
    """Vivliostyle PDF生成サービス"""
    
    def __init__(self):
        # テンプレートディレクトリ
        self.templates_dir = Path(__file__).parent.parent.parent / "templates"
        
        # Jinja2環境を設定
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True
        )
    
    async def generate_pdf(
        self,
        template_name: str,
        data: Dict[str, Any],
        output_path: Path,
        vivliostyle_options: Dict[str, Any] = None
    ) -> Path:
        """PDFを生成
        
        Args:
            template_name: テンプレート名（例: "memoir"）
            data: テンプレートに渡すデータ
            output_path: 出力PDFパス
            vivliostyle_options: Vivliostyle CLIオプション
                - format: "pdf" (デフォルト)
                - size: "A4", "A5", "B5", "letter" など (デフォルト: "A4")
                - crop_marks: True/False (トンボ表示)
                - bleed: "3mm" (裁ち落とし)
                - css: "path/to/custom.css" (追加CSS)
                - single_doc: True/False (デフォルト: True)
                - timeout: 60 (秒)
        
        Returns:
            生成されたPDFファイルのパス
        """
        
        if vivliostyle_options is None:
            vivliostyle_options = {}
        
        # 一時ディレクトリを作成
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                # 1. 画像を処理（ダウンロード＆コピー）
                if data.get("cover_image"):
                    cover_image_local = await self._process_image(data["cover_image"], temp_path, "cover")
                    if cover_image_local:
                        data["cover_image"] = cover_image_local
                        logger.info(f"カバー画像を処理: {cover_image_local}")
                    else:
                        # 画像処理失敗の場合は画像なしで続行
                        logger.warning("カバー画像の処理に失敗しました")
                        data["cover_image"] = None
                
                # 年表の画像も処理
                if data.get("timeline"):
                    for i, item in enumerate(data["timeline"]):
                        if item.get("image"):
                            image_local = await self._process_image(item["image"], temp_path, f"timeline_{i}")
                            if image_local:
                                item["image"] = image_local
                                logger.info(f"年表画像{i}を処理: {image_local}")
                            else:
                                # 画像処理失敗の場合は画像なしで続行
                                logger.warning(f"年表画像{i}の処理に失敗しました")
                                item["image"] = None
                
                # 2. HTMLファイルを保存（画像処理後）
                html_content = self._render_template(template_name, data)
                html_file = temp_path / "index.html"
                with open(html_file, "w", encoding="utf-8") as f:
                    f.write(html_content)
                
                logger.info(f"HTMLファイル作成: {html_file}")
                
                # 3. Vivliostyle CLIでPDF生成（一時ディレクトリ内）
                temp_pdf = temp_path / "output.pdf"
                await self._generate_pdf_with_vivliostyle(html_file, temp_pdf, vivliostyle_options)
                
                # 4. PDFを最終的な出力先にコピー
                logger.info(f"PDFを出力先にコピー: {temp_pdf} -> {output_path}")
                shutil.copy2(temp_pdf, output_path)
                
                logger.info(f"PDF生成完了: {output_path}")
                return output_path
                
            except Exception as e:
                logger.error(f"PDF生成エラー: {str(e)}")
                raise
    
    async def _process_image(
        self,
        image_path: str,
        temp_dir: Path,
        prefix: str = "image"
    ) -> str:
        """画像を処理（ダウンロードまたはコピー）
        
        Args:
            image_path: 画像パス（URLまたはローカルパス）
            temp_dir: 一時ディレクトリ
            prefix: ファイル名のプレフィックス
        
        Returns:
            相対パス（ファイル名のみ）
        """
        try:
            # ローカルメディアファイルURLの場合、file_idを抽出してローカルパスを取得
            if "/media/image/" in image_path or "/media/file/" in image_path:
                logger.info(f"ローカルメディアファイル検出: {image_path}")
                # URLからfile_idを抽出
                parts = image_path.split("/media/")
                if len(parts) > 1:
                    file_id = parts[1].split("/")[-1]
                    logger.info(f"ファイルID抽出: {file_id}")
                    
                    # file_serviceを使ってローカルパスを取得
                    from ..services.file_service import file_service
                    from ..config import settings
                    
                    file_metadata = file_service.get_file_by_id(file_id)
                    if file_metadata:
                        # uploadsディレクトリからの相対パスを絶対パスに変換
                        uploads_dir = Path(settings.UPLOADS_DIR)
                        source_path = uploads_dir / file_metadata['stored_filename']
                        
                        if source_path.exists():
                            dest_path = temp_dir / f"{prefix}{source_path.suffix}"
                            shutil.copy2(source_path, dest_path)
                            logger.info(f"ローカル画像をコピー: {source_path} -> {dest_path.name}")
                            return dest_path.name
                        else:
                            logger.warning(f"ファイルが見つかりません: {source_path}")
                            return None
                    else:
                        logger.warning(f"メタデータが見つかりません: {file_id}")
                        # フォールバックとしてHTTPダウンロードを試みる
                        pass
            
            if image_path.startswith(("http://", "https://")):
                # 外部URLの場合：ダウンロード
                logger.info(f"画像をダウンロード: {image_path}")
                response = requests.get(image_path, timeout=30)
                response.raise_for_status()
                
                # 拡張子を取得（Content-Typeから推測）
                content_type = response.headers.get("Content-Type", "")
                if "jpeg" in content_type or "jpg" in content_type:
                    ext = ".jpg"
                elif "png" in content_type:
                    ext = ".png"
                elif "gif" in content_type:
                    ext = ".gif"
                else:
                    ext = ".jpg"  # デフォルト
                
                dest_path = temp_dir / f"{prefix}{ext}"
                with open(dest_path, "wb") as f:
                    f.write(response.content)
                
                logger.info(f"画像をダウンロード完了: {dest_path.name}")
                return dest_path.name
            else:
                # ローカルファイルの場合：コピー
                source_path = Path(image_path)
                if source_path.exists():
                    dest_path = temp_dir / f"{prefix}{source_path.suffix}"
                    shutil.copy2(source_path, dest_path)
                    logger.info(f"画像をコピー: {dest_path.name}")
                    return dest_path.name
                else:
                    logger.warning(f"画像ファイルが見つかりません: {image_path}")
                    return None
        except Exception as e:
            logger.error(f"画像処理エラー: {image_path}, {str(e)}")
            return None
    
    def _render_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """Jinja2テンプレートをレンダリング
        
        Args:
            template_name: テンプレート名
            data: テンプレートデータ
        
        Returns:
            レンダリングされたHTML
        """
        try:
            template = self.jinja_env.get_template(f"{template_name}/template.html")
            html_content = template.render(**data)
            logger.info(f"テンプレートレンダリング完了: {template_name}")
            return html_content
        except Exception as e:
            logger.error(f"テンプレートレンダリングエラー: {str(e)}")
            raise Exception(f"テンプレートレンダリングに失敗しました: {str(e)}")
    
    async def _generate_pdf_with_vivliostyle(
        self,
        html_file: Path,
        output_file: Path,
        options: Dict[str, Any] = None
    ) -> None:
        """Vivliostyle CLIでPDFを生成
        
        Args:
            html_file: 入力HTMLファイルパス
            output_file: 出力PDFファイルパス
            options: Vivliostyleオプション
        """
        
        if options is None:
            options = {}
        
        # Vivliostyle CLIコマンドを構築
        cmd = [
            "vivliostyle",
            "build",
            str(html_file),
            "--output", str(output_file),
        ]
        
        # フォーマット（デフォルト: pdf）
        cmd.extend(["--format", options.get("format", "pdf")])
        
        # サイズ（デフォルト: A4）
        cmd.extend(["--size", options.get("size", "A4")])
        
        # single-doc（デフォルト: True）
        if options.get("single_doc", True):
            cmd.append("--single-doc")
        
        # トンボ（crop marks）
        if options.get("crop_marks", False):
            cmd.append("--crop-marks")
        
        # 裁ち落とし（bleed）
        if "bleed" in options:
            cmd.extend(["--bleed", options["bleed"]])
        
        # 追加CSS
        if "css" in options:
            cmd.extend(["--css", options["css"]])
        
        # タイムアウト（デフォルト: 60秒）
        timeout = options.get("timeout", 60)
        
        logger.info(f"Vivliostyle CLI実行: {' '.join(cmd)}")
        logger.info(f"作業ディレクトリ: {html_file.parent}")
        logger.info(f"HTMLファイル存在確認: {html_file.exists()}")
        logger.info(f"出力ファイルパス: {output_file}")
        
        try:
            # 非同期でコマンド実行
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(html_file.parent)  # HTMLファイルのディレクトリで実行
            )
            
            # タイムアウト
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            # 標準出力・標準エラーをログ出力
            stdout_str = stdout.decode() if stdout else ""
            stderr_str = stderr.decode() if stderr else ""
            
            logger.info(f"Vivliostyle stdout: {stdout_str}")
            if stderr_str:
                logger.warning(f"Vivliostyle stderr: {stderr_str}")
            
            logger.info(f"Vivliostyle returncode: {process.returncode}")
            logger.info(f"PDFファイル存在確認: {output_file.exists()}")
            
            if process.returncode != 0:
                error_msg = stderr_str if stderr_str else "Unknown error"
                logger.error(f"Vivliostyle CLIエラー（returncode={process.returncode}）: {error_msg}")
                raise RuntimeError(f"Vivliostyle CLIエラー（returncode={process.returncode}）: {error_msg}")
            
            if not output_file.exists():
                # HTMLファイルの内容も確認
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content_preview = f.read()[:500]
                    logger.error(f"HTMLファイルプレビュー: {html_content_preview}")
                
                raise RuntimeError(
                    f"PDFファイルが生成されませんでした。\n"
                    f"stdout: {stdout_str}\n"
                    f"stderr: {stderr_str}"
                )
            
            logger.info(f"Vivliostyle CLI完了: {output_file}")
            logger.info(f"PDFファイルサイズ: {output_file.stat().st_size} bytes")
            
        except asyncio.TimeoutError:
            logger.error(f"Vivliostyle CLIがタイムアウトしました（{timeout}秒）")
            raise RuntimeError(f"Vivliostyle CLIがタイムアウトしました（{timeout}秒）")
        except FileNotFoundError:
            logger.error("Vivliostyle CLIが見つかりません")
            raise RuntimeError(
                "Vivliostyle CLIが見つかりません。インストールされているか確認してください。\n"
                "インストール: npm install -g @vivliostyle/cli"
            )
        except Exception as e:
            logger.error(f"Vivliostyle CLI実行エラー: {str(e)}")
            raise RuntimeError(f"Vivliostyle CLI実行エラー: {str(e)}")


# グローバルインスタンス
vivliostyle_service = VivliostyleService()

