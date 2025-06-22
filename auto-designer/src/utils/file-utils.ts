import * as fs from 'fs';
import * as path from 'path';

/**
 * ファイルが存在するかチェック
 */
export function fileExists(filePath: string): boolean {
  return fs.existsSync(filePath);
}

/**
 * ディレクトリが存在するかチェック
 */
export function directoryExists(dirPath: string): boolean {
  return fs.existsSync(dirPath) && fs.statSync(dirPath).isDirectory();
}

/**
 * ディレクトリを作成（存在しない場合）
 */
export function ensureDirectoryExists(dirPath: string): void {
  if (!directoryExists(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

/**
 * ファイルを読み込み
 */
export function readFile(filePath: string): string {
  if (!fileExists(filePath)) {
    throw new Error(`File not found: ${filePath}`);
  }
  return fs.readFileSync(filePath, 'utf-8');
}

/**
 * ファイルを書き込み
 */
export function writeFile(filePath: string, content: string): void {
  const dir = path.dirname(filePath);
  ensureDirectoryExists(dir);
  fs.writeFileSync(filePath, content, 'utf-8');
}

/**
 * JSONファイルを読み込み
 */
export function readJsonFile<T>(filePath: string): T {
  const content = readFile(filePath);
  return JSON.parse(content) as T;
}

/**
 * JSONファイルを書き込み
 */
export function writeJsonFile<T>(filePath: string, data: T): void {
  const content = JSON.stringify(data, null, 2);
  writeFile(filePath, content);
}

/**
 * ファイル拡張子を取得
 */
export function getFileExtension(filePath: string): string {
  return path.extname(filePath).toLowerCase();
}

/**
 * ファイル名（拡張子なし）を取得
 */
export function getFileNameWithoutExtension(filePath: string): string {
  return path.basename(filePath, path.extname(filePath));
}

/**
 * 出力ディレクトリのパスを取得
 */
export function getOutputPath(fileName: string): string {
  return path.join(process.cwd(), 'output', fileName);
} 