import fs from 'fs';
import path from 'path';
import sharp from 'sharp';

export interface ImageInfo {
  id: string;
  originalName: string;
  fileName: string;
  path: string;
  size: number;
  width: number;
  height: number;
  mimeType: string;
  uploadedAt: Date;
}

export class ImageManager {
  private uploadDir: string;
  private maxFileSize: number = 10 * 1024 * 1024; // 10MB
  private allowedMimeTypes: string[] = [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp'
  ];

  constructor(uploadDir: string = 'uploads') {
    this.uploadDir = path.resolve(uploadDir);
    this.ensureUploadDir();
  }

  private ensureUploadDir(): void {
    if (!fs.existsSync(this.uploadDir)) {
      fs.mkdirSync(this.uploadDir, { recursive: true });
    }
  }

  private generateImageId(): string {
    return `img_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private validateFile(file: any): { valid: boolean; error?: string } {
    if (!file) {
      return { valid: false, error: 'ファイルが選択されていません' };
    }

    if (file.size > this.maxFileSize) {
      return { valid: false, error: `ファイルサイズが大きすぎます（最大${this.maxFileSize / 1024 / 1024}MB）` };
    }

    if (!this.allowedMimeTypes.includes(file.mimetype)) {
      return { valid: false, error: 'サポートされていないファイル形式です' };
    }

    return { valid: true };
  }

  async saveImage(file: any): Promise<ImageInfo> {
    const validation = this.validateFile(file);
    if (!validation.valid) {
      throw new Error(validation.error);
    }

    const imageId = this.generateImageId();
    const extension = path.extname(file.filename || 'image.jpg');
    const fileName = `${imageId}${extension}`;
    const filePath = path.join(this.uploadDir, fileName);

    // ファイルを保存
    await file.file.pipe(fs.createWriteStream(filePath));

    // 画像情報を取得
    const imageBuffer = fs.readFileSync(filePath);
    const metadata = await sharp(imageBuffer).metadata();

    const imageInfo: ImageInfo = {
      id: imageId,
      originalName: file.filename || 'unknown',
      fileName: fileName,
      path: filePath,
      size: file.size,
      width: metadata.width || 0,
      height: metadata.height || 0,
      mimeType: file.mimetype,
      uploadedAt: new Date()
    };

    return imageInfo;
  }

  async optimizeImage(imagePath: string, options: {
    width?: number;
    height?: number;
    quality?: number;
    format?: 'jpeg' | 'png' | 'webp';
  } = {}): Promise<Buffer> {
    const {
      width,
      height,
      quality = 80,
      format = 'jpeg'
    } = options;

    let sharpInstance = sharp(imagePath);

    if (width || height) {
      sharpInstance = sharpInstance.resize(width, height, {
        fit: 'inside',
        withoutEnlargement: true
      });
    }

    switch (format) {
      case 'jpeg':
        sharpInstance = sharpInstance.jpeg({ quality });
        break;
      case 'png':
        sharpInstance = sharpInstance.png({ quality });
        break;
      case 'webp':
        sharpInstance = sharpInstance.webp({ quality });
        break;
    }

    return await sharpInstance.toBuffer();
  }

  async getImageBuffer(imagePath: string): Promise<Buffer> {
    if (!fs.existsSync(imagePath)) {
      throw new Error('画像ファイルが見つかりません');
    }
    return fs.readFileSync(imagePath);
  }

  async deleteImage(imagePath: string): Promise<void> {
    if (fs.existsSync(imagePath)) {
      fs.unlinkSync(imagePath);
    }
  }

  getImageUrl(fileName: string): string {
    return `/images/${fileName}`;
  }

  listImages(): ImageInfo[] {
    const images: ImageInfo[] = [];
    const files = fs.readdirSync(this.uploadDir);
    
    for (const file of files) {
      const filePath = path.join(this.uploadDir, file);
      const stats = fs.statSync(filePath);
      
      if (stats.isFile() && /\.(jpg|jpeg|png|gif|webp)$/i.test(file)) {
        // 基本的な情報のみ取得（詳細情報は必要に応じて）
        images.push({
          id: path.parse(file).name,
          originalName: file,
          fileName: file,
          path: filePath,
          size: stats.size,
          width: 0, // 必要に応じて取得
          height: 0, // 必要に応じて取得
          mimeType: this.getMimeType(file),
          uploadedAt: stats.mtime
        });
      }
    }
    
    return images;
  }

  private getMimeType(fileName: string): string {
    const ext = path.extname(fileName).toLowerCase();
    const mimeTypes: { [key: string]: string } = {
      '.jpg': 'image/jpeg',
      '.jpeg': 'image/jpeg',
      '.png': 'image/png',
      '.gif': 'image/gif',
      '.webp': 'image/webp'
    };
    return mimeTypes[ext] || 'application/octet-stream';
  }
} 