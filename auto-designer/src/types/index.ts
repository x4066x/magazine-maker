// 雑誌データの型定義
export interface MagazineData {
  title: string;
  subtitle?: string;
  author: string;
  date: string;
  content: MagazineContent[];
  coverImage?: string;
  theme?: string;
}

export interface MagazineContent {
  type: 'text' | 'image' | 'heading' | 'quote';
  content: string;
  style?: {
    fontSize?: string;
    fontWeight?: string;
    color?: string;
    alignment?: 'left' | 'center' | 'right';
  };
}

// 請求書データの型定義
export interface InvoiceData {
  invoiceNumber: string;
  date: string;
  dueDate: string;
  client: {
    name: string;
    address: string;
    email: string;
  };
  items: InvoiceItem[];
  subtotal: number;
  tax: number;
  total: number;
  notes?: string;
}

export interface InvoiceItem {
  description: string;
  quantity: number;
  unitPrice: number;
  amount: number;
}

// 自分史データの型定義
export interface MemoirData {
  title: string;
  subtitle?: string;
  author: string;
  birthDate: string;
  birthPlace: string;
  occupation?: string;
  interests?: string[];
  motto?: string;
  profileImage?: string;
  timeline: TimelineEvent[];
}

export interface TimelineEvent {
  year: number;
  title: string;
  description: string;
  image?: string;
  imageCaption?: string;
}

// PDF生成オプション
export interface PDFOptions {
  format?: 'A4' | 'Letter' | 'Legal';
  orientation?: 'portrait' | 'landscape';
  margin?: {
    top: string;
    right: string;
    bottom: string;
    left: string;
  };
  outputPath?: string;
}

// テンプレート設定
export interface TemplateConfig {
  name: string;
  path: string;
  dataType: 'magazine' | 'invoice' | 'memoir';
  options?: PDFOptions;
} 