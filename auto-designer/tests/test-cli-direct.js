const { generateSampleHtml } = require('./src/pdf-cli');
const fs = require('fs');
const path = require('path');

async function testPagedjsCli() {
  try {
    console.log('🚀 pagedjs-cli 直接テスト開始');
    
    // 請求書サンプルデータ
    const invoiceData = {
      customerName: "株式会社テスト商事",
      customerAddress: "〒100-0001 東京都千代田区千代田1-2-3",
      customerPhone: "03-1234-5678",
      invoiceNumber: "INV-2024-001",
      issueDate: "2024-01-15",
      dueDate: "2024-02-14",
      taxRate: 0.1,
      items: [
        {
          name: "Webサイト制作",
          quantity: 1,
          price: 500000
        },
        {
          name: "サーバー構築",
          quantity: 1,
          price: 300000
        }
      ],
      notes: "お支払いは銀行振込にてお願いいたします。"
    };

    // HTMLファイルを生成
    console.log('📝 HTMLファイル生成中...');
    const html = await generateSampleHtml('invoice', invoiceData);
    
    // 一時HTMLファイルを保存
    const htmlPath = path.join(__dirname, 'temp', 'invoice-test.html');
    const tempDir = path.dirname(htmlPath);
    
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true });
    }
    
    fs.writeFileSync(htmlPath, html);
    console.log(`✅ HTMLファイル保存: ${htmlPath}`);
    
    // pagedjs-cliでPDF生成
    console.log('📄 PDF生成中...');
    const { execSync } = require('child_process');
    const outputPath = path.join(__dirname, 'test-output', 'invoice-cli-direct.pdf');
    
    const command = `npx pagedjs-cli "${htmlPath}" -o "${outputPath}"`;
    console.log(`実行コマンド: ${command}`);
    
    execSync(command, { 
      cwd: __dirname,
      stdio: 'inherit'
    });
    
    // 結果確認
    if (fs.existsSync(outputPath)) {
      const stats = fs.statSync(outputPath);
      console.log(`✅ PDF生成成功: ${outputPath} (${stats.size} bytes)`);
    } else {
      console.log('❌ PDFファイルが生成されませんでした');
    }
    
  } catch (error) {
    console.error('❌ エラー:', error);
  }
}

testPagedjsCli(); 