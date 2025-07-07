# v2 API ガイド

## 概要

v2 APIは、memoirテンプレートをベースにしたPDF生成APIです。テンプレート指定とJSON形式のデータを入力することで、美しい自分史PDFを生成できます。

## エンドポイント一覧

### 1. ヘルスチェック
```
GET /v2/health
```

**レスポンス例:**
```json
{
  "status": "ok",
  "version": "2.0.0",
  "timestamp": "2024-12-19T10:30:00.000Z",
  "features": ["memoir-pdf-generation"]
}
```

### 2. テンプレート情報取得
```
GET /v2/templates
```

**レスポンス例:**
```json
{
  "templates": [
    {
      "id": "memoir",
      "name": "自分史",
      "description": "人生の歩みを時系列で記録する自分史テンプレート",
      "version": "2.0.0",
      "dataSchema": {
        "title": "string (必須)",
        "subtitle": "string (オプション)",
        "author": "string (必須)",
        "date": "string (オプション)",
        "profile": {
          "name": "string (必須)",
          "birthDate": "string (オプション)",
          "birthPlace": "string (オプション)",
          "currentLocation": "string (オプション)",
          "occupation": "string (オプション)",
          "hobbies": "string[] (オプション)",
          "profileImage": "string (オプション)",
          "description": "string (オプション)"
        },
        "timeline": [
          {
            "year": "number (必須)",
            "title": "string (必須)",
            "description": "string (必須)",
            "image": "string (オプション)",
            "imageCaption": "string (オプション)",
            "tags": "string[] (オプション)"
          }
        ],
        "chapters": [
          {
            "title": "string (必須)",
            "content": "string (必須)",
            "pageBreak": "boolean (オプション)"
          }
        ]
      }
    }
  ]
}
```

### 3. サンプルデータ取得
```
GET /v2/samples/memoir
```

**レスポンス例:**
```json
{
  "success": true,
  "data": {
    "title": "私の人生の歩み",
    "subtitle": "〜これまでの道のり〜",
    "author": "田中太郎",
    "date": "2024年12月",
    "profile": {
      "name": "田中太郎",
      "birthDate": "1985年3月15日",
      "birthPlace": "東京都",
      "currentLocation": "神奈川県横浜市",
      "occupation": "ソフトウェアエンジニア",
      "hobbies": ["読書", "旅行", "写真撮影"],
      "description": "IT業界で20年以上働くエンジニア。新しい技術を学ぶことが好きで、常に自己啓発を心がけています。"
    },
    "timeline": [
      {
        "year": 1985,
        "title": "誕生",
        "description": "東京都で生まれました。両親と兄の4人家族で育ちました。",
        "tags": ["誕生", "家族"]
      }
    ],
    "chapters": [
      {
        "title": "幼少期",
        "content": "幼い頃は好奇心旺盛で、様々なことに興味を持っていました。",
        "pageBreak": true
      }
    ]
  },
  "description": "memoirテンプレート用のサンプルデータです。このデータを参考に、ご自身のデータを作成してください。"
}
```

### 4. PDF生成
```
POST /v2/pdf
```

**リクエスト例:**
```json
{
  "template": "memoir",
  "data": {
    "title": "私の人生の歩み",
    "subtitle": "〜これまでの道のり〜",
    "author": "田中太郎",
    "date": "2024年12月",
    "profile": {
      "name": "田中太郎",
      "birthDate": "1985年3月15日",
      "birthPlace": "東京都",
      "currentLocation": "神奈川県横浜市",
      "occupation": "ソフトウェアエンジニア",
      "hobbies": ["読書", "旅行", "写真撮影"],
      "description": "IT業界で20年以上働くエンジニア。新しい技術を学ぶことが好きで、常に自己啓発を心がけています。"
    },
    "timeline": [
      {
        "year": 1985,
        "title": "誕生",
        "description": "東京都で生まれました。両親と兄の4人家族で育ちました。",
        "tags": ["誕生", "家族"]
      },
      {
        "year": 1991,
        "title": "小学校入学",
        "description": "地元の公立小学校に入学。友達と一緒に楽しく学校生活を送りました。",
        "tags": ["教育", "学校"]
      },
      {
        "year": 2003,
        "title": "大学入学",
        "description": "情報工学を専攻し、プログラミングの基礎を学びました。",
        "tags": ["教育", "大学", "プログラミング"]
      },
      {
        "year": 2007,
        "title": "就職",
        "description": "IT企業に就職し、ソフトウェアエンジニアとしてのキャリアをスタートしました。",
        "tags": ["就職", "キャリア", "IT"]
      },
      {
        "year": 2015,
        "title": "結婚",
        "description": "妻と出会い、結婚式を挙げました。新しい家族との生活が始まりました。",
        "tags": ["結婚", "家族"]
      },
      {
        "year": 2020,
        "title": "転職",
        "description": "より大きなプロジェクトに携わるため、新しい会社に転職しました。",
        "tags": ["転職", "キャリア"]
      }
    ],
    "chapters": [
      {
        "title": "幼少期",
        "content": "幼い頃は好奇心旺盛で、様々なことに興味を持っていました。特に科学や機械に興味があり、よくおもちゃを分解しては組み立て直していました。",
        "pageBreak": true
      },
      {
        "title": "学生時代",
        "content": "学生時代は部活動に熱中し、多くの友達と出会いました。勉強も頑張り、希望の大学に進学することができました。",
        "pageBreak": true
      },
      {
        "title": "社会人として",
        "content": "社会人になってからは、多くの困難に直面しましたが、仲間と協力して乗り越えてきました。技術の進歩に合わせて、常に新しいことを学び続けています。"
      }
    ],
    "metadata": {
      "keywords": ["自分史", "人生", "キャリア", "IT"],
      "category": "自伝",
      "version": "1.0"
    }
  },
  "options": {
    "format": "A4",
    "margin": "20mm 15mm 25mm 15mm"
  }
}
```

**成功レスポンス:**
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename="memoir-1702987200000.pdf"`
- レスポンスボディ: PDFファイルのバイナリデータ

**エラーレスポンス例:**
```json
{
  "success": false,
  "error": {
    "message": "データの形式が正しくありません",
    "code": "INVALID_DATA_FORMAT",
    "details": "authorは必須の文字列です"
  }
}
```

## データ構造の詳細

### MemoirData インターフェース

```typescript
interface MemoirData {
  title: string;                    // 必須: 自分史のタイトル
  subtitle?: string;                // オプション: サブタイトル
  author: string;                   // 必須: 著者名
  date?: string;                    // オプション: 作成日
  profile: {                        // 必須: プロフィール情報
    name: string;                   // 必須: 名前
    birthDate?: string;             // オプション: 生年月日
    birthPlace?: string;            // オプション: 出生地
    currentLocation?: string;       // オプション: 現在の居住地
    occupation?: string;            // オプション: 職業
    hobbies?: string[];             // オプション: 趣味の配列
    profileImage?: string;          // オプション: プロフィール画像（ファイル名またはBase64）
    description?: string;           // オプション: 自己紹介
  };
  timeline: Array<{                 // 必須: 年表データ
    year: number;                   // 必須: 年
    title: string;                  // 必須: イベントタイトル
    description: string;            // 必須: イベントの詳細説明
    image?: string;                 // オプション: 画像（ファイル名またはBase64）
    imageCaption?: string;          // オプション: 画像のキャプション
    tags?: string[];                // オプション: タグの配列
  }>;
  chapters?: Array<{                // オプション: 章の配列
    title: string;                  // 必須: 章のタイトル
    content: string;                // 必須: 章の内容
    pageBreak?: boolean;            // オプション: ページ区切り
  }>;
  metadata?: {                      // オプション: メタデータ
    keywords?: string[];            // オプション: キーワード
    category?: string;              // オプション: カテゴリ
    version?: string;               // オプション: バージョン
  };
}
```

## 画像の扱い

### 画像ファイルの指定方法

1. **ファイル名指定**: アップロード済みの画像ファイル名を指定
   ```json
   {
     "profileImage": "profile.jpg"
   }
   ```

2. **パス指定**: `/images/` または `uploads/` パスで指定
   ```json
   {
     "profileImage": "/images/profile.jpg"
   }
   ```

3. **Base64データ**: 直接Base64エンコードされたデータを指定
   ```json
   {
     "profileImage": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
   }
   ```

### 画像の自動処理

APIは画像パスを自動的に検出し、Base64エンコードしてPDFに埋め込みます。これにより、PDFファイルは画像に依存せずに配布できます。

## エラーコード一覧

| コード | 説明 |
|--------|------|
| `MISSING_TEMPLATE` | テンプレート名が指定されていません |
| `UNSUPPORTED_TEMPLATE` | サポートされていないテンプレートです |
| `MISSING_DATA` | データが指定されていません |
| `INVALID_DATA_FORMAT` | データの形式が正しくありません |
| `PDF_GENERATION_ERROR` | PDF生成中にエラーが発生しました |

## 使用例

### cURLでの使用例

```bash
# サンプルデータを取得
curl -X GET http://localhost:3000/v2/samples/memoir

# PDFを生成
curl -X POST http://localhost:3000/v2/pdf \
  -H "Content-Type: application/json" \
  -d @memoir-data.json \
  --output memoir.pdf
```

### JavaScriptでの使用例

```javascript
// サンプルデータを取得
const sampleResponse = await fetch('http://localhost:3000/v2/samples/memoir');
const sampleData = await sampleResponse.json();

// PDFを生成
const pdfResponse = await fetch('http://localhost:3000/v2/pdf', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    template: 'memoir',
    data: sampleData.data
  })
});

if (pdfResponse.ok) {
  const pdfBlob = await pdfResponse.blob();
  const url = URL.createObjectURL(pdfBlob);
  
  // PDFをダウンロード
  const a = document.createElement('a');
  a.href = url;
  a.download = 'memoir.pdf';
  a.click();
}
```

### Pythonでの使用例

```python
import requests
import json

# サンプルデータを取得
sample_response = requests.get('http://localhost:3000/v2/samples/memoir')
sample_data = sample_response.json()

# PDFを生成
pdf_response = requests.post('http://localhost:3000/v2/pdf', 
  json={
    'template': 'memoir',
    'data': sample_data['data']
  }
)

if pdf_response.status_code == 200:
  # PDFを保存
  with open('memoir.pdf', 'wb') as f:
    f.write(pdf_response.content)
  print('PDFが生成されました: memoir.pdf')
else:
  print('エラー:', pdf_response.json())
```

## 注意事項

1. **必須フィールド**: `title`, `author`, `profile.name`, `timeline`は必須です
2. **timeline**: 少なくとも1つの項目が必要です
3. **画像サイズ**: 大きな画像は自動的に最適化されます
4. **文字数制限**: 長いテキストは自動的に改ページされます
5. **特殊文字**: UTF-8エンコーディングで日本語が正しく表示されます
6. **PDF生成オプション**: pagedjs-cli版では`margin`オプションはサポートされていません（CSSの`@page`ルールで制御）
7. **ページサイズ**: `format`オプションは`--page-size`として内部的に処理されます

## トラブルシューティング

### よくあるエラー

1. **MISSING_TEMPLATE**: テンプレート名を指定してください
2. **INVALID_DATA_FORMAT**: データ構造を確認してください
3. **PDF_GENERATION_ERROR**: サーバーのログを確認してください

### デバッグ方法

1. まず `/v2/health` でAPIの状態を確認
2. `/v2/samples/memoir` でサンプルデータを取得
3. サンプルデータを基に自分のデータを作成
4. エラーが発生した場合はレスポンスの詳細を確認

## 技術的改善点（2025年1月30日更新）

### pagedjs-cliオプション修正
- **ページサイズ指定**: `--format` → `--page-size`に修正
- **マージン制御**: CSSの`@page`ルールで制御（オプション削除）
- **エラー解決**: 「unknown option '--format'」エラーを解決

### エラーハンドリング強化
- **Content-Typeチェック**: レスポンスのContent-Typeを適切に検証
- **JSONエラーレスポンス**: エラー時の詳細情報をJSON形式で提供
- **デバッグ情報**: エラー原因の特定を容易にするログ出力

### LINE Bot連携改善
- **reply_token対応**: 30秒制限に対応したPush message自動切り替え
- **非同期処理**: PDF生成の非同期化による応答性向上
- **エラー回復**: エラー発生時の適切なフォールバック処理 