import Fastify from 'fastify';
import { generatePdf, generateHtml } from './pdf';
import { generatePdfWithCli } from './pdf-cli';
import { ImageManager, ImageInfo } from './utils/image-manager';
import fs from 'fs';
import path from 'path';

// リクエストボディの型定義
interface PdfRequest {
  template: string;
  data: any;
  fileName?: string;
  options?: {
    format?: 'A4' | 'A3' | 'Letter' | 'Legal';
    margin?: {
      top?: string;
      right?: string;
      bottom?: string;
      left?: string;
    };
    printBackground?: boolean;
  };
}

interface ImageUploadRequest {
  imageData: string; // Base64エンコードされた画像データ
  fileName?: string;
  mimeType?: string;
}

// レスポンスの型定義
interface ErrorResponse {
  error: string;
  details?: string;
  timestamp: string;
}

const fastify = Fastify({
  logger: {
    level: 'info'
  }
});

// 画像マネージャーの初期化
const imageManager = new ImageManager('uploads');

// ヘルスチェックエンドポイント
fastify.get('/health', async (request, reply) => {
  return { status: 'ok', timestamp: new Date().toISOString() };
});

// 利用可能なテンプレート一覧を取得
fastify.get('/templates', async (request, reply) => {
  try {
    const templatesDir = path.join(__dirname, 'templates');
    const files = fs.readdirSync(templatesDir);
    const templates = files
      .filter(file => file.endsWith('.eta'))
      .map(file => file.replace('.eta', ''));
    
    return {
      templates,
      count: templates.length
    };
  } catch (error) {
    fastify.log.error('テンプレート一覧取得エラー:', error);
    reply.status(500).send({
      error: 'テンプレート一覧の取得に失敗しました',
      timestamp: new Date().toISOString()
    } as ErrorResponse);
  }
});

// 画像アップロードエンドポイント（Base64方式）
fastify.post('/upload/image', async (request, reply) => {
  try {
    const { imageData, fileName, mimeType } = request.body as ImageUploadRequest;
    
    if (!imageData) {
      return reply.status(400).send({
        error: '画像データが指定されていません',
        timestamp: new Date().toISOString()
      } as ErrorResponse);
    }
    
    // Base64データをバッファに変換
    const buffer = Buffer.from(imageData, 'base64');
    
    // 画像情報を作成
    const imageId = `img_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const extension = mimeType ? mimeType.split('/')[1] : 'jpg';
    const finalFileName = `${imageId}.${extension}`;
    const filePath = path.join(imageManager['uploadDir'], finalFileName);
    
    // ファイルを保存
    fs.writeFileSync(filePath, buffer);
    
    // 画像情報を取得
    const metadata = await imageManager['optimizeImage'](filePath, {});
    
    const imageInfo: ImageInfo = {
      id: imageId,
      originalName: fileName || 'uploaded-image',
      fileName: finalFileName,
      path: filePath,
      size: buffer.length,
      width: 0, // 必要に応じて取得
      height: 0, // 必要に応じて取得
      mimeType: mimeType || 'image/jpeg',
      uploadedAt: new Date()
    };
    
    fastify.log.info(`画像アップロード完了: ${imageInfo.originalName} -> ${imageInfo.fileName}`);
    
    return {
      success: true,
      image: {
        id: imageInfo.id,
        fileName: imageInfo.fileName,
        url: imageManager.getImageUrl(imageInfo.fileName),
        size: imageInfo.size,
        width: imageInfo.width,
        height: imageInfo.height,
        uploadedAt: imageInfo.uploadedAt
      }
    };
    
  } catch (error) {
    fastify.log.error('画像アップロードエラー:', error);
    
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    
    reply.status(500).send({
      error: '画像アップロード中にエラーが発生しました',
      details: errorMessage,
      timestamp: new Date().toISOString()
    } as ErrorResponse);
  }
});

// 画像一覧取得エンドポイント
fastify.get('/images', async (request, reply) => {
  try {
    const images = imageManager.listImages();
    
    return {
      images: images.map(img => ({
        id: img.id,
        fileName: img.fileName,
        url: imageManager.getImageUrl(img.fileName),
        size: img.size,
        width: img.width,
        height: img.height,
        uploadedAt: img.uploadedAt
      })),
      count: images.length
    };
    
  } catch (error) {
    fastify.log.error('画像一覧取得エラー:', error);
    
    reply.status(500).send({
      error: '画像一覧の取得に失敗しました',
      timestamp: new Date().toISOString()
    } as ErrorResponse);
  }
});

// 画像表示エンドポイント
fastify.get('/images/:fileName', async (request, reply) => {
  try {
    const { fileName } = request.params as { fileName: string };
    const imagePath = path.join(imageManager['uploadDir'], fileName);
    
    if (!fs.existsSync(imagePath)) {
      return reply.status(404).send({
        error: '画像が見つかりません',
        timestamp: new Date().toISOString()
      } as ErrorResponse);
    }
    
    const buffer = await imageManager.getImageBuffer(imagePath);
    const mimeType = imageManager['getMimeType'](fileName);
    
    reply
      .header('Content-Type', mimeType)
      .header('Cache-Control', 'public, max-age=31536000')
      .send(buffer);
      
  } catch (error) {
    fastify.log.error('画像表示エラー:', error);
    
    reply.status(500).send({
      error: '画像の表示に失敗しました',
      timestamp: new Date().toISOString()
    } as ErrorResponse);
  }
});

// 自分史プレビューエンドポイント
fastify.post('/memoir/preview', async (request, reply) => {
  try {
    const { data } = request.body as { data: any };
    
    if (!data) {
      return reply.status(400).send({
        error: 'データが指定されていません',
        timestamp: new Date().toISOString()
      } as ErrorResponse);
    }
    
    // テンプレートファイルの存在確認
    const templatePath = path.join(__dirname, 'templates', 'memoir.eta');
    if (!fs.existsSync(templatePath)) {
      return reply.status(400).send({
        error: '自分史テンプレートが見つかりません',
        timestamp: new Date().toISOString()
      } as ErrorResponse);
    }
    
    // 画像をBase64エンコードして埋め込み
    const uploadDir = path.join(process.cwd(), 'uploads');
    const processedData = await embedImagesAsBase64(data, uploadDir);
    
    // HTMLプレビューを生成
    const html = await generateHtml('memoir', processedData);
    
    reply
      .header('Content-Type', 'text/html; charset=utf-8')
      .send(html);
      
  } catch (error) {
    fastify.log.error('自分史プレビュー生成エラー:', error);
    
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    
    reply.status(500).send({
      error: '自分史プレビューの生成に失敗しました',
      details: errorMessage,
      timestamp: new Date().toISOString()
    } as ErrorResponse);
  }
});

// 画像をBase64エンコードする関数
async function embedImagesAsBase64(data: any, uploadDir: string): Promise<any> {
  const processedData = { ...data };
  
  // プロフィール画像の処理
  if (processedData.profileImage) {
    let imagePath: string;
    
    if (processedData.profileImage.startsWith('/images/')) {
      // /images/パスの場合
      imagePath = path.join(uploadDir, processedData.profileImage.replace('/images/', ''));
    } else if (processedData.profileImage.startsWith('uploads/')) {
      // uploads/パスの場合
      imagePath = path.join(process.cwd(), processedData.profileImage);
    } else {
      // その他のパスの場合
      imagePath = path.join(uploadDir, processedData.profileImage);
    }
    
    if (fs.existsSync(imagePath)) {
      const imageBuffer = fs.readFileSync(imagePath);
      const mimeType = getMimeType(imagePath);
      processedData.profileImage = `data:${mimeType};base64,${imageBuffer.toString('base64')}`;
    }
  }
  
  // 年表画像の処理
  if (processedData.timeline) {
    for (const item of processedData.timeline) {
      if (item.image) {
        let imagePath: string;
        
        if (item.image.startsWith('/images/')) {
          // /images/パスの場合
          imagePath = path.join(uploadDir, item.image.replace('/images/', ''));
        } else if (item.image.startsWith('uploads/')) {
          // uploads/パスの場合
          imagePath = path.join(process.cwd(), item.image);
        } else {
          // その他のパスの場合
          imagePath = path.join(uploadDir, item.image);
        }
        
        if (fs.existsSync(imagePath)) {
          const imageBuffer = fs.readFileSync(imagePath);
          const mimeType = getMimeType(imagePath);
          item.image = `data:${mimeType};base64,${imageBuffer.toString('base64')}`;
        }
      }
    }
  }
  
  return processedData;
}

// MIMEタイプを取得する関数
function getMimeType(filePath: string): string {
  const ext = path.extname(filePath).toLowerCase();
  const mimeTypes: { [key: string]: string } = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.webp': 'image/webp'
  };
  return mimeTypes[ext] || 'image/jpeg';
}

// PDF生成エンドポイント（puppeteer版）
fastify.post('/pdf', async (request, reply) => {
  const startTime = Date.now();
  
  try {
    const { template, data, fileName, options } = request.body as PdfRequest;
    
    // バリデーション
    if (!template) {
      return reply.status(400).send({
        error: 'テンプレート名が指定されていません',
        timestamp: new Date().toISOString()
      } as ErrorResponse);
    }
    
    if (!data) {
      return reply.status(400).send({
        error: 'データが指定されていません',
        timestamp: new Date().toISOString()
      } as ErrorResponse);
    }
    
    // テンプレートファイルの存在確認
    const templatePath = path.join(__dirname, 'templates', `${template}.eta`);
    if (!fs.existsSync(templatePath)) {
      return reply.status(400).send({
        error: `テンプレート '${template}' が見つかりません`,
        details: '利用可能なテンプレートは /templates エンドポイントで確認できます',
        timestamp: new Date().toISOString()
      } as ErrorResponse);
    }
    
    fastify.log.info(`PDF生成開始: テンプレート=${template}, ファイル名=${fileName || 'output.pdf'}`);
    
    // PDF生成
    const buffer = await generatePdf(template, data, options, embedImagesAsBase64);
    
    const processingTime = Date.now() - startTime;
    fastify.log.info(`PDF生成完了: ${processingTime}ms, サイズ=${buffer.length} bytes`);
    
    // レスポンスヘッダー設定
    const finalFileName = fileName || `${template}-${Date.now()}.pdf`;
    
    reply
      .header('Content-Type', 'application/pdf')
      .header('Content-Disposition', `attachment; filename="${finalFileName}"`)
      .header('Content-Length', buffer.length.toString())
      .header('X-Processing-Time', processingTime.toString())
      .send(buffer);
      
  } catch (error) {
    const processingTime = Date.now() - startTime;
    fastify.log.error(`PDF生成エラー (${processingTime}ms):`, error);
    
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    
    reply.status(500).send({
      error: 'PDF生成中にエラーが発生しました',
      details: errorMessage,
      timestamp: new Date().toISOString()
    } as ErrorResponse);
  }
});

// PDF生成エンドポイント（pagedjs-cli版）
fastify.post('/pdf/cli', async (request, reply) => {
  const startTime = Date.now();
  
  try {
    const { template, data, fileName, options } = request.body as PdfRequest;
    
    // バリデーション
    if (!template) {
      return reply.status(400).send({
        error: 'テンプレート名が指定されていません',
        timestamp: new Date().toISOString()
      } as ErrorResponse);
    }
    
    if (!data) {
      return reply.status(400).send({
        error: 'データが指定されていません',
        timestamp: new Date().toISOString()
      } as ErrorResponse);
    }
    
    // テンプレートファイルの存在確認
    const templatePath = path.join(__dirname, 'templates', `${template}.eta`);
    if (!fs.existsSync(templatePath)) {
      return reply.status(400).send({
        error: `テンプレート '${template}' が見つかりません`,
        details: '利用可能なテンプレートは /templates エンドポイントで確認できます',
        timestamp: new Date().toISOString()
      } as ErrorResponse);
    }
    
    fastify.log.info(`PDF生成開始 (CLI): テンプレート=${template}, ファイル名=${fileName || 'output.pdf'}`);
    
    // pagedjs-cliオプションを変換
    const cliOptions = {
      format: options?.format,
      margin: options?.margin ? `${options.margin.top} ${options.margin.right} ${options.margin.bottom} ${options.margin.left}` : undefined
    };
    
    // PDF生成（pagedjs-cli版）
    const buffer = await generatePdfWithCli(template, data, cliOptions, embedImagesAsBase64);
    
    const processingTime = Date.now() - startTime;
    fastify.log.info(`PDF生成完了 (CLI): ${processingTime}ms, サイズ=${buffer.length} bytes`);
    
    // レスポンスヘッダー設定
    const finalFileName = fileName || `${template}-cli-${Date.now()}.pdf`;
    
    reply
      .header('Content-Type', 'application/pdf')
      .header('Content-Disposition', `attachment; filename="${finalFileName}"`)
      .header('Content-Length', buffer.length.toString())
      .header('X-Processing-Time', processingTime.toString())
      .header('X-Generator', 'pagedjs-cli')
      .send(buffer);
      
  } catch (error) {
    const processingTime = Date.now() - startTime;
    fastify.log.error(`PDF生成エラー (CLI) (${processingTime}ms):`, error);
    
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    
    reply.status(500).send({
      error: 'PDF生成中にエラーが発生しました (CLI)',
      details: errorMessage,
      timestamp: new Date().toISOString()
    } as ErrorResponse);
  }
});

// エラーハンドラー
fastify.setErrorHandler((error, request, reply) => {
  fastify.log.error('未処理エラー:', error);
  
  reply.status(500).send({
    error: 'サーバー内部エラーが発生しました',
    timestamp: new Date().toISOString()
  } as ErrorResponse);
});

// 404ハンドラー
fastify.setNotFoundHandler((request, reply) => {
  reply.status(404).send({
    error: 'エンドポイントが見つかりません',
    details: `Path: ${request.url}`,
    timestamp: new Date().toISOString()
  } as ErrorResponse);
});

const start = async () => {
  try {
    const port = parseInt(process.env.PORT || '3000');
    const host = process.env.HOST || '0.0.0.0';
    
    await fastify.listen({ port, host });
    
    console.log(`🚀 サーバーが起動しました: http://localhost:${port}`);
    console.log(`📋 ヘルスチェック: http://localhost:${port}/health`);
    console.log(`📝 テンプレート一覧: http://localhost:${port}/templates`);
    console.log(`📄 PDF生成: POST http://localhost:${port}/pdf`);
    console.log(`🖼️ 画像アップロード: POST http://localhost:${port}/upload/image`);
    console.log(`🖼️ 画像一覧: GET http://localhost:${port}/images`);
    console.log(`📖 自分史プレビュー: POST http://localhost:${port}/memoir/preview`);
    
  } catch (err) {
    fastify.log.error('サーバー起動エラー:', err);
    process.exit(1);
  }
};

start(); 