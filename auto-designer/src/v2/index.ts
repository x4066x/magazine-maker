import { FastifyInstance } from 'fastify';
import { generatePdfWithCli } from '../pdf-cli';
import { embedImagesAsBase64 } from '../utils/image-embedder';
import path from 'path';
import fs from 'fs';

// v2 API用のデータ型定義
export interface MemoirData {
  title: string;
  subtitle?: string;
  author: string;
  date?: string;
  profile: {
    name: string;
    birthDate?: string;
    birthPlace?: string;
    currentLocation?: string;
    occupation?: string;
    hobbies?: string[];
    profileImage?: string; // 画像ファイル名またはBase64データ
    description?: string;
  };
  timeline: Array<{
    year: number;
    title: string;
    description: string;
    image?: string; // 画像ファイル名またはBase64データ
    imageCaption?: string;
    tags?: string[];
  }>;
  chapters?: Array<{
    title: string;
    content: string;
    pageBreak?: boolean;
  }>;
  metadata?: {
    keywords?: string[];
    category?: string;
    version?: string;
  };
}

export interface V2PdfRequest {
  template: 'memoir';
  data: MemoirData;
  options?: {
    format?: 'A4' | 'A3' | 'Letter' | 'Legal';
    margin?: string;
    output?: string;
  };
}

export interface V2PdfResponse {
  success: boolean;
  data?: {
    pdfBuffer: Buffer;
    fileName: string;
    size: number;
    processingTime: number;
  };
  error?: {
    message: string;
    details?: string;
    code?: string;
  };
}

// v2 APIルーター
export async function v2Routes(fastify: FastifyInstance) {
  // v2 APIのヘルスチェック
  fastify.get('/v2/health', async (request, reply) => {
    return {
      status: 'ok',
      version: '2.0.0',
      timestamp: new Date().toISOString(),
      features: ['memoir-pdf-generation']
    };
  });

  // テンプレート情報取得
  fastify.get('/v2/templates', async (request, reply) => {
    return {
      templates: [
        {
          id: 'memoir',
          name: '自分史',
          description: '人生の歩みを時系列で記録する自分史テンプレート',
          version: '2.0.0',
          dataSchema: {
            title: 'string (必須)',
            subtitle: 'string (オプション)',
            author: 'string (必須)',
            date: 'string (オプション)',
            profile: {
              name: 'string (必須)',
              birthDate: 'string (オプション)',
              birthPlace: 'string (オプション)',
              currentLocation: 'string (オプション)',
              occupation: 'string (オプション)',
              hobbies: 'string[] (オプション)',
              profileImage: 'string (オプション)',
              description: 'string (オプション)'
            },
            timeline: [
              {
                year: 'number (必須)',
                title: 'string (必須)',
                description: 'string (必須)',
                image: 'string (オプション)',
                imageCaption: 'string (オプション)',
                tags: 'string[] (オプション)'
              }
            ],
            chapters: [
              {
                title: 'string (必須)',
                content: 'string (必須)',
                pageBreak: 'boolean (オプション)'
              }
            ]
          }
        }
      ]
    };
  });

  // v2 PDF生成エンドポイント
  fastify.post('/v2/pdf', async (request, reply) => {
    const startTime = Date.now();
    
    try {
      const { template, data, options } = request.body as V2PdfRequest;
      
      // バリデーション
      if (!template) {
        return reply.status(400).send({
          success: false,
          error: {
            message: 'テンプレート名が指定されていません',
            code: 'MISSING_TEMPLATE'
          }
        } as V2PdfResponse);
      }
      
      if (template !== 'memoir') {
        return reply.status(400).send({
          success: false,
          error: {
            message: `テンプレート '${template}' はサポートされていません`,
            code: 'UNSUPPORTED_TEMPLATE',
            details: '現在サポートされているテンプレート: memoir'
          }
        } as V2PdfResponse);
      }
      
      if (!data) {
        return reply.status(400).send({
          success: false,
          error: {
            message: 'データが指定されていません',
            code: 'MISSING_DATA'
          }
        } as V2PdfResponse);
      }
      
      // memoirデータのバリデーション
      const validationError = validateMemoirData(data);
      if (validationError) {
        return reply.status(400).send({
          success: false,
          error: {
            message: 'データの形式が正しくありません',
            code: 'INVALID_DATA_FORMAT',
            details: validationError
          }
        } as V2PdfResponse);
      }
      
      fastify.log.info(`v2 PDF生成開始: テンプレート=${template}`);
      
      // PDF生成
      const pdfBuffer = await generatePdfWithCli(
        template,
        data,
        options,
        embedImagesAsBase64
      );
      
      const processingTime = Date.now() - startTime;
      const fileName = `memoir-${Date.now()}.pdf`;
      
      fastify.log.info(`v2 PDF生成完了: ${processingTime}ms, サイズ=${pdfBuffer.length} bytes`);
      
      // レスポンスヘッダー設定
      reply
        .header('Content-Type', 'application/pdf')
        .header('Content-Disposition', `attachment; filename="${fileName}"`)
        .header('Content-Length', pdfBuffer.length.toString())
        .header('X-Processing-Time', processingTime.toString())
        .header('X-API-Version', '2.0.0');
      
      // PDFバッファを直接送信
      return reply.send(pdfBuffer);
      
    } catch (error) {
      const processingTime = Date.now() - startTime;
      fastify.log.error(`v2 PDF生成エラー (${processingTime}ms):`, error);
      
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      
      return reply.status(500).send({
        success: false,
        error: {
          message: 'PDF生成中にエラーが発生しました',
          details: errorMessage,
          code: 'PDF_GENERATION_ERROR'
        }
      } as V2PdfResponse);
    }
  });

  // サンプルデータ取得エンドポイント
  fastify.get('/v2/samples/memoir', async (request, reply) => {
    const sampleData: MemoirData = {
      title: '私の人生の歩み',
      subtitle: '〜これまでの道のり〜',
      author: '田中太郎',
      date: '2024年12月',
      profile: {
        name: '田中太郎',
        birthDate: '1985年3月15日',
        birthPlace: '東京都',
        currentLocation: '神奈川県横浜市',
        occupation: 'ソフトウェアエンジニア',
        hobbies: ['読書', '旅行', '写真撮影'],
        description: 'IT業界で20年以上働くエンジニア。新しい技術を学ぶことが好きで、常に自己啓発を心がけています。'
      },
      timeline: [
        {
          year: 1985,
          title: '誕生',
          description: '東京都で生まれました。両親と兄の4人家族で育ちました。',
          tags: ['誕生', '家族']
        },
        {
          year: 1991,
          title: '小学校入学',
          description: '地元の公立小学校に入学。友達と一緒に楽しく学校生活を送りました。',
          tags: ['教育', '学校']
        },
        {
          year: 2003,
          title: '大学入学',
          description: '情報工学を専攻し、プログラミングの基礎を学びました。',
          tags: ['教育', '大学', 'プログラミング']
        },
        {
          year: 2007,
          title: '就職',
          description: 'IT企業に就職し、ソフトウェアエンジニアとしてのキャリアをスタートしました。',
          tags: ['就職', 'キャリア', 'IT']
        },
        {
          year: 2015,
          title: '結婚',
          description: '妻と出会い、結婚式を挙げました。新しい家族との生活が始まりました。',
          tags: ['結婚', '家族']
        },
        {
          year: 2020,
          title: '転職',
          description: 'より大きなプロジェクトに携わるため、新しい会社に転職しました。',
          tags: ['転職', 'キャリア']
        }
      ],
      chapters: [
        {
          title: '幼少期',
          content: '幼い頃は好奇心旺盛で、様々なことに興味を持っていました。特に科学や機械に興味があり、よくおもちゃを分解しては組み立て直していました。',
          pageBreak: true
        },
        {
          title: '学生時代',
          content: '学生時代は部活動に熱中し、多くの友達と出会いました。勉強も頑張り、希望の大学に進学することができました。',
          pageBreak: true
        },
        {
          title: '社会人として',
          content: '社会人になってからは、多くの困難に直面しましたが、仲間と協力して乗り越えてきました。技術の進歩に合わせて、常に新しいことを学び続けています。'
        }
      ],
      metadata: {
        keywords: ['自分史', '人生', 'キャリア', 'IT'],
        category: '自伝',
        version: '1.0'
      }
    };
    
    return {
      success: true,
      data: sampleData,
      description: 'memoirテンプレート用のサンプルデータです。このデータを参考に、ご自身のデータを作成してください。'
    };
  });
}

// memoirデータのバリデーション関数
function validateMemoirData(data: any): string | null {
  if (!data.title || typeof data.title !== 'string') {
    return 'titleは必須の文字列です';
  }
  
  if (!data.author || typeof data.author !== 'string') {
    return 'authorは必須の文字列です';
  }
  
  if (!data.profile || typeof data.profile !== 'object') {
    return 'profileは必須のオブジェクトです';
  }
  
  if (!data.profile.name || typeof data.profile.name !== 'string') {
    return 'profile.nameは必須の文字列です';
  }
  
  if (!data.timeline || !Array.isArray(data.timeline)) {
    return 'timelineは必須の配列です';
  }
  
  if (data.timeline.length === 0) {
    return 'timelineは少なくとも1つの項目が必要です';
  }
  
  for (let i = 0; i < data.timeline.length; i++) {
    const item = data.timeline[i];
    if (!item.year || typeof item.year !== 'number') {
      return `timeline[${i}].yearは必須の数値です`;
    }
    if (!item.title || typeof item.title !== 'string') {
      return `timeline[${i}].titleは必須の文字列です`;
    }
    if (!item.description || typeof item.description !== 'string') {
      return `timeline[${i}].descriptionは必須の文字列です`;
    }
  }
  
  return null;
} 