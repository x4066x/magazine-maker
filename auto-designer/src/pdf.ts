import { launch, Browser, Page } from 'puppeteer-core';
import { renderFile } from 'eta';
import path from 'path';
import fs from 'fs';

interface PagedWindow extends Window {
  Paged: {
    Previewer: new () => {
      preview: () => Promise<void>;
    };
  };
}

interface PdfOptions {
  format?: 'A4' | 'A3' | 'Letter' | 'Legal';
  margin?: {
    top?: string;
    right?: string;
    bottom?: string;
    left?: string;
  };
  printBackground?: boolean;
}

export async function generateHtml(
  template: string, 
  data: any
): Promise<string> {
  const templatePath = path.join(__dirname, 'templates', `${template}.eta`);
  const html = await renderFile(templatePath, data);
  if (!html) throw new Error('テンプレートのレンダリングに失敗しました');
  return html;
}

export async function generatePdf(
  template: string, 
  data: any, 
  options: PdfOptions = {},
  embedImagesAsBase64?: (data: any, uploadDir: string) => Promise<any>
): Promise<Buffer> {
  const templatePath = path.join(__dirname, 'templates', `${template}.eta`);
  
  // 画像をBase64エンコードして埋め込み（関数が提供されている場合）
  let processedData = data;
  if (embedImagesAsBase64) {
    console.log('Base64埋め込み処理を開始します...');
    const uploadDir = path.join(process.cwd(), 'uploads');
    processedData = await embedImagesAsBase64(data, uploadDir);
    console.log('Base64埋め込み処理が完了しました');
  } else {
    console.log('embedImagesAsBase64関数が提供されていません');
  }
  
  const html = await renderFile(templatePath, processedData);
  if (!html) throw new Error('テンプレートのレンダリングに失敗しました');

  let browser: Browser | null = null;
  let page: Page | null = null;

  try {
    browser = await launch({
      headless: true,
      executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--no-first-run',
        '--no-zygote',
        '--disable-gpu'
      ]
    });
    
    page = await browser.newPage();
    
    // ページの設定
    await page.setViewport({ width: 1200, height: 800 });
    
    // 画像の読み込みを待つ設定
    await page.setRequestInterception(true);
    page.on('request', (request) => {
      request.continue();
    });
    
    await page.setContent(html, { waitUntil: 'networkidle0' });
    
    // 画像の読み込み完了を待つ
    await page.waitForFunction(() => {
      const images = document.querySelectorAll('img');
      return Array.from(images).every(img => img.complete && img.naturalHeight > 0);
    }, { timeout: 30000 });
    
    // Paged.js を読み込み
    await page.addScriptTag({ 
      url: 'https://unpkg.com/pagedjs/dist/paged.polyfill.js' 
    });
    
    // Paged.js の設定
    await page.evaluate(() => {
      (window as any).PagedConfig = {
        auto: false,
        beforePreview: (content: any) => {
          console.log('Paged.js preview starting...');
        },
        afterPreview: (pages: any) => {
          console.log(`Generated ${pages.length} pages`);
        }
      };
    });
    
    // Paged.js の処理を実行
    await page.evaluate(() => {
      return new ((window as unknown) as PagedWindow).Paged.Previewer().preview();
    });
    
    // ページ分割処理の完了を待つ
    await page.waitForFunction(() => {
      return document.querySelectorAll('.pagedjs_page').length > 0;
    }, { timeout: 10000 });
    
    // PDF生成オプション
    const pdfOptions = {
      format: options.format || 'A4',
      printBackground: options.printBackground !== false,
      margin: {
        top: options.margin?.top || '20mm',
        right: options.margin?.right || '20mm',
        bottom: options.margin?.bottom || '20mm',
        left: options.margin?.left || '20mm'
      }
    };
    
    const buffer = await page.pdf(pdfOptions);
    
    if (!buffer || buffer.length === 0) {
      throw new Error('PDFの生成に失敗しました');
    }
    
    return buffer;
    
  } catch (error) {
    console.error('PDF生成エラー:', error);
    throw new Error(`PDF生成中にエラーが発生しました: ${error instanceof Error ? error.message : 'Unknown error'}`);
  } finally {
    if (page) {
      try {
        await page.close();
      } catch (error) {
        console.error('ページクローズエラー:', error);
      }
    }
    if (browser) {
      try {
        await browser.close();
      } catch (error) {
        console.error('ブラウザクローズエラー:', error);
      }
    }
  }
} 