#!/usr/bin/env node

/**
 * HTMLからPDFを生成するスクリプト
 * Puppeteerを使用してHTMLファイルをPDFに変換します
 */

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

// 出力ディレクトリの作成
const outputDir = path.join(__dirname, 'output');
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

// テンプレートの設定
const templates = [
  {
    name: 'タイトルページ',
    input: 'sample/templates/modern/title/modern-title-page/index.html',
    output: 'output/title-page.pdf'
  },
  {
    name: '片面ページ',
    input: 'sample/templates/modern/single/modern-minimal-single/index.html',
    output: 'output/single-page.pdf'
  },
  {
    name: '見開きページ',
    input: 'sample/templates/modern/spread/modern-balanced-spread/index.html',
    output: 'output/spread-page.pdf'
  }
];

// 非同期で待機する関数
function wait(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// 画像をBase64エンコードする関数
function imageToBase64(imagePath) {
  try {
    const imageBuffer = fs.readFileSync(imagePath);
    const ext = path.extname(imagePath).toLowerCase();
    let mimeType = 'image/jpeg';
    
    if (ext === '.png') {
      mimeType = 'image/png';
    } else if (ext === '.gif') {
      mimeType = 'image/gif';
    } else if (ext === '.webp') {
      mimeType = 'image/webp';
    }
    
    return `data:${mimeType};base64,${imageBuffer.toString('base64')}`;
  } catch (error) {
    console.error(`画像の読み込みエラー: ${imagePath}`, error);
    return null;
  }
}

async function generatePDF() {
  console.log('🎨 PDF生成を開始します...');
  
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  try {
    for (const template of templates) {
      console.log(`📄 ${template.name}のPDFを生成中...`);
      
      const inputPath = path.join(__dirname, template.input);
      const outputPath = path.join(__dirname, template.output);
      
      if (!fs.existsSync(inputPath)) {
        console.log(`❌ 入力ファイルが見つかりません: ${inputPath}`);
        continue;
      }

      const page = await browser.newPage();
      
      // HTMLファイルを読み込み
      let htmlContent = fs.readFileSync(inputPath, 'utf8');
      
      // CSSファイルのパスを絶対パスに変更
      const templateDir = path.dirname(inputPath);
      const cssPath = path.join(templateDir, 'style.css');
      
      if (fs.existsSync(cssPath)) {
        const cssContent = fs.readFileSync(cssPath, 'utf8');
        // CSSをHTMLに直接埋め込み
        htmlContent = htmlContent.replace(
          '<link rel="stylesheet" href="style.css">',
          `<style>${cssContent}</style>`
        );
        console.log(`  📝 CSSファイルを埋め込みました: ${cssPath}`);
      }
      
      // 画像パスを絶対パスに変更
      const imagesDir = path.join(__dirname, 'sample/images');
      console.log(`  🖼️ 画像ディレクトリ: ${imagesDir}`);
      
      // 相対パスの画像をBase64に変換
      htmlContent = htmlContent.replace(
        /src="\.\.\/\.\.\/\.\.\/\.\.\/images\/([^"]+)"/g,
        (match, filename) => {
          const fullImagePath = path.join(imagesDir, filename);
          console.log(`    📷 画像をBase64に変換中: ${filename}`);
          
          if (fs.existsSync(fullImagePath)) {
            const base64Data = imageToBase64(fullImagePath);
            if (base64Data) {
              console.log(`      ✅ Base64変換成功: ${filename}`);
              return `src="${base64Data}"`;
            } else {
              console.log(`      ❌ Base64変換失敗: ${filename}`);
              return match;
            }
          } else {
            console.log(`      ❌ 画像ファイルが見つかりません: ${fullImagePath}`);
            return match;
          }
        }
      );
      
      htmlContent = htmlContent.replace(
        /src="\.\.\/\.\.\/\.\.\/images\/([^"]+)"/g,
        (match, filename) => {
          const fullImagePath = path.join(imagesDir, filename);
          console.log(`    📷 画像をBase64に変換中: ${filename}`);
          
          if (fs.existsSync(fullImagePath)) {
            const base64Data = imageToBase64(fullImagePath);
            if (base64Data) {
              console.log(`      ✅ Base64変換成功: ${filename}`);
              return `src="${base64Data}"`;
            } else {
              console.log(`      ❌ Base64変換失敗: ${filename}`);
              return match;
            }
          } else {
            console.log(`      ❌ 画像ファイルが見つかりません: ${fullImagePath}`);
            return match;
          }
        }
      );
      
      // デバッグ用：変換後のHTMLを確認
      console.log(`  🔍 変換後のHTMLの画像パス:`);
      const imgMatches = htmlContent.match(/src="[^"]*"/g);
      if (imgMatches) {
        imgMatches.forEach(match => {
          if (match.includes('data:')) {
            console.log(`    ${match.substring(0, 50)}... (Base64データ)`);
          } else {
            console.log(`    ${match}`);
          }
        });
      }
      
      await page.setContent(htmlContent, {
        waitUntil: 'networkidle0'
      });

      // 画像の読み込みを待つ
      await wait(1000);

      // PDFを生成
      await page.pdf({
        path: outputPath,
        format: 'A4',
        printBackground: true,
        margin: {
          top: '0',
          right: '0',
          bottom: '0',
          left: '0'
        }
      });

      await page.close();
      console.log(`✅ ${template.output} が生成されました`);
    }

    console.log('\n🎉 すべてのPDFの生成が完了しました！');
    console.log('\n📁 出力ファイル:');
    templates.forEach(template => {
      console.log(`  - ${template.output}`);
    });

  } catch (error) {
    console.error('❌ エラーが発生しました:', error);
  } finally {
    await browser.close();
  }
}

// スクリプトを実行
generatePDF().catch(console.error);
