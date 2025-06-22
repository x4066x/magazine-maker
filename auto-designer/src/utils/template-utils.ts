import { renderFile } from 'eta';
import * as path from 'path';
import { fileExists, readFile } from './file-utils';
import { MagazineData, InvoiceData, TemplateConfig } from '../types';

/**
 * テンプレートファイルのパスを取得
 */
export function getTemplatePath(templateName: string): string {
  const templatePath = path.join(process.cwd(), 'src', 'templates', `${templateName}.eta`);
  if (!fileExists(templatePath)) {
    throw new Error(`Template not found: ${templateName}`);
  }
  return templatePath;
}

/**
 * テンプレートを読み込み
 */
export function loadTemplate(templateName: string): string {
  const templatePath = getTemplatePath(templateName);
  return readFile(templatePath);
}

/**
 * 雑誌テンプレートをレンダリング
 */
export async function renderMagazineTemplate(data: MagazineData): Promise<string> {
  try {
    const templatePath = getTemplatePath('magazine');
    return await renderFile(templatePath, data);
  } catch (error) {
    throw new Error(`Failed to render magazine template: ${error}`);
  }
}

/**
 * 請求書テンプレートをレンダリング
 */
export async function renderInvoiceTemplate(data: InvoiceData): Promise<string> {
  try {
    const templatePath = getTemplatePath('invoice');
    return await renderFile(templatePath, data);
  } catch (error) {
    throw new Error(`Failed to render invoice template: ${error}`);
  }
}

/**
 * テンプレート設定を取得
 */
export function getTemplateConfig(templateName: string): TemplateConfig {
  const configs: Record<string, TemplateConfig> = {
    magazine: {
      name: 'magazine',
      path: 'magazine.eta',
      dataType: 'magazine',
      options: {
        format: 'A4',
        orientation: 'portrait',
        margin: {
          top: '20mm',
          right: '20mm',
          bottom: '20mm',
          left: '20mm'
        }
      }
    },
    invoice: {
      name: 'invoice',
      path: 'invoice.eta',
      dataType: 'invoice',
      options: {
        format: 'A4',
        orientation: 'portrait',
        margin: {
          top: '15mm',
          right: '15mm',
          bottom: '15mm',
          left: '15mm'
        }
      }
    }
  };

  const config = configs[templateName];
  if (!config) {
    throw new Error(`Unknown template: ${templateName}`);
  }

  return config;
}

/**
 * 利用可能なテンプレート一覧を取得
 */
export function getAvailableTemplates(): string[] {
  return ['magazine', 'invoice'];
}

/**
 * テンプレートの検証
 */
export function validateTemplateData(templateName: string, data: any): boolean {
  const config = getTemplateConfig(templateName);
  
  switch (config.dataType) {
    case 'magazine':
      return validateMagazineData(data);
    case 'invoice':
      return validateInvoiceData(data);
    default:
      return false;
  }
}

/**
 * 雑誌データの検証
 */
function validateMagazineData(data: any): data is MagazineData {
  return (
    typeof data === 'object' &&
    typeof data.title === 'string' &&
    typeof data.author === 'string' &&
    typeof data.date === 'string' &&
    Array.isArray(data.content)
  );
}

/**
 * 請求書データの検証
 */
function validateInvoiceData(data: any): data is InvoiceData {
  return (
    typeof data === 'object' &&
    typeof data.invoiceNumber === 'string' &&
    typeof data.date === 'string' &&
    typeof data.dueDate === 'string' &&
    typeof data.client === 'object' &&
    Array.isArray(data.items) &&
    typeof data.subtotal === 'number' &&
    typeof data.tax === 'number' &&
    typeof data.total === 'number'
  );
} 