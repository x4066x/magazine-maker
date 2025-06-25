import fs from 'fs';
import path from 'path';

/**
 * 画像をBase64エンコードしてデータに埋め込む関数
 * @param data 元のデータオブジェクト
 * @param uploadDir アップロードディレクトリのパス
 * @returns 画像がBase64エンコードされたデータオブジェクト
 */
export async function embedImagesAsBase64(data: any, uploadDir: string): Promise<any> {
  const processedData = { ...data };
  
  // プロフィール画像の処理
  if (processedData.profileImage) {
    processedData.profileImage = await processImagePath(processedData.profileImage, uploadDir);
  }
  
  // 年表画像の処理
  if (processedData.timeline) {
    for (const item of processedData.timeline) {
      if (item.image) {
        item.image = await processImagePath(item.image, uploadDir);
      }
    }
  }
  
  // chapters内の画像処理（将来の拡張用）
  if (processedData.chapters) {
    for (const chapter of processedData.chapters) {
      if (chapter.image) {
        chapter.image = await processImagePath(chapter.image, uploadDir);
      }
    }
  }
  
  return processedData;
}

/**
 * 画像パスを処理してBase64エンコードされたデータURLに変換
 * @param imagePath 画像パス
 * @param uploadDir アップロードディレクトリのパス
 * @returns Base64エンコードされたデータURLまたは元のパス
 */
async function processImagePath(imagePath: string, uploadDir: string): Promise<string> {
  // 既にBase64データURLの場合はそのまま返す
  if (imagePath.startsWith('data:')) {
    return imagePath;
  }
  
  let resolvedPath: string;
  
  if (imagePath.startsWith('/images/')) {
    // /images/パスの場合
    resolvedPath = path.join(uploadDir, imagePath.replace('/images/', ''));
  } else if (imagePath.startsWith('uploads/')) {
    // uploads/パスの場合
    resolvedPath = path.join(process.cwd(), imagePath);
  } else {
    // その他のパスの場合
    resolvedPath = path.join(uploadDir, imagePath);
  }
  
  if (fs.existsSync(resolvedPath)) {
    try {
      const imageBuffer = fs.readFileSync(resolvedPath);
      const mimeType = getMimeType(resolvedPath);
      return `data:${mimeType};base64,${imageBuffer.toString('base64')}`;
    } catch (error) {
      console.warn(`画像ファイルの読み込みに失敗しました: ${resolvedPath}`, error);
      return imagePath; // エラーの場合は元のパスを返す
    }
  }
  
  return imagePath; // ファイルが存在しない場合は元のパスを返す
}

/**
 * ファイルパスからMIMEタイプを取得
 * @param filePath ファイルパス
 * @returns MIMEタイプ
 */
function getMimeType(filePath: string): string {
  const ext = path.extname(filePath).toLowerCase();
  const mimeTypes: { [key: string]: string } = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.webp': 'image/webp',
    '.svg': 'image/svg+xml',
    '.bmp': 'image/bmp',
    '.tiff': 'image/tiff',
    '.tif': 'image/tiff'
  };
  return mimeTypes[ext] || 'image/jpeg';
}

/**
 * 画像ファイルの存在確認
 * @param imagePath 画像パス
 * @param uploadDir アップロードディレクトリのパス
 * @returns ファイルが存在するかどうか
 */
export function imageExists(imagePath: string, uploadDir: string): boolean {
  if (imagePath.startsWith('data:')) {
    return true; // Base64データは存在するとみなす
  }
  
  let resolvedPath: string;
  
  if (imagePath.startsWith('/images/')) {
    resolvedPath = path.join(uploadDir, imagePath.replace('/images/', ''));
  } else if (imagePath.startsWith('uploads/')) {
    resolvedPath = path.join(process.cwd(), imagePath);
  } else {
    resolvedPath = path.join(uploadDir, imagePath);
  }
  
  return fs.existsSync(resolvedPath);
}

/**
 * 画像ファイルの情報を取得
 * @param imagePath 画像パス
 * @param uploadDir アップロードディレクトリのパス
 * @returns 画像ファイルの情報
 */
export function getImageInfo(imagePath: string, uploadDir: string): { exists: boolean; size?: number; mimeType?: string } {
  if (imagePath.startsWith('data:')) {
    return { exists: true, mimeType: 'data-url' };
  }
  
  let resolvedPath: string;
  
  if (imagePath.startsWith('/images/')) {
    resolvedPath = path.join(uploadDir, imagePath.replace('/images/', ''));
  } else if (imagePath.startsWith('uploads/')) {
    resolvedPath = path.join(process.cwd(), imagePath);
  } else {
    resolvedPath = path.join(uploadDir, imagePath);
  }
  
  if (fs.existsSync(resolvedPath)) {
    const stats = fs.statSync(resolvedPath);
    return {
      exists: true,
      size: stats.size,
      mimeType: getMimeType(resolvedPath)
    };
  }
  
  return { exists: false };
} 