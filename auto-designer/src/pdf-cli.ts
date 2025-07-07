import { renderFile } from 'eta';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import fs from 'fs';

const execAsync = promisify(exec);

interface PdfCliOptions {
  format?: 'A4' | 'A3' | 'Letter' | 'Legal';
  margin?: string;
  output?: string;
}

export async function generatePdfWithCli(
  template: string,
  data: any,
  options: PdfCliOptions = {},
  embedImagesAsBase64?: (data: any, uploadDir: string) => Promise<any>
): Promise<Buffer> {
  // 画像をBase64エンコードして埋め込み（機能が提供されている場合）
  let processedData = data;
  if (embedImagesAsBase64) {
    const uploadDir = path.join(process.cwd(), 'uploads');
    processedData = await embedImagesAsBase64(data, uploadDir);
  }

  const templatePath = path.join(__dirname, 'templates', `${template}.eta`);
  const html = await renderFile(templatePath, processedData);
  if (!html) throw new Error('テンプレートのレンダリングに失敗しました');

  // 一時HTMLファイルを作成
  const tempDir = path.join(__dirname, '..', 'temp');
  if (!fs.existsSync(tempDir)) {
    fs.mkdirSync(tempDir, { recursive: true });
  }

  const timestamp = Date.now();
  const htmlFilePath = path.join(tempDir, `${template}-${timestamp}.html`);
  const outputPath = options.output || path.join(tempDir, `${template}-${timestamp}.pdf`);

  try {
    // HTMLファイルを保存
    fs.writeFileSync(htmlFilePath, html);

    // pagedjs-cliコマンドを構築
    const cliArgs = [
      htmlFilePath,
      '-o', outputPath
    ];

    if (options.format) {
      cliArgs.push('--page-size', options.format);
    }

    const command = `npx pagedjs-cli ${cliArgs.join(' ')}`;
    console.log(`実行コマンド: ${command}`);

    // pagedjs-cliを実行
    const { stdout, stderr } = await execAsync(command, {
      cwd: path.join(__dirname, '..'),
      timeout: 30000 // 30秒タイムアウト
    });

    if (stderr) {
      console.warn('pagedjs-cli警告:', stderr);
    }

    console.log('pagedjs-cli出力:', stdout);

    // 生成されたPDFファイルを読み込み
    if (!fs.existsSync(outputPath)) {
      throw new Error(`PDFファイルが生成されませんでした: ${outputPath}`);
    }

    const pdfBuffer = fs.readFileSync(outputPath);
    
    if (!pdfBuffer || pdfBuffer.length === 0) {
      throw new Error('PDFファイルが空です');
    }

    // HTMLファイルのみ即座に削除（PDFファイルは保持）
    try {
      if (fs.existsSync(htmlFilePath)) {
        fs.unlinkSync(htmlFilePath);
      }
    } catch (cleanupError) {
      console.warn('HTMLファイルのクリーンアップに失敗:', cleanupError);
    }

    return pdfBuffer;

  } catch (error) {
    console.error('pagedjs-cli実行エラー:', error);
    throw new Error(`pagedjs-cliでのPDF生成に失敗しました: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

// サンプルHTMLファイルを生成する関数（テスト用）
export async function generateSampleHtml(template: string, data: any): Promise<string> {
  const templatePath = path.join(__dirname, 'templates', `${template}.eta`);
  const html = await renderFile(templatePath, data);
  if (!html) throw new Error('テンプレートのレンダリングに失敗しました');
  return html;
} 