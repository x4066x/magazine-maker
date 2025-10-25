# 拡張版簡易フロー - 実装ガイド

## 🎯 概要

**拡張版簡易フロー**は、従来の簡易フロー（タイトル+カバー写真）を拡張し、表紙PDFを即座に生成した後、見開きページと単一ページの画像を順次収集して、完全版の自分史PDFを生成する新しいフローです。

## 🔄 フロー全体像

```
👤 ユーザー: 「作る」「作成」（トリガーワード）
   ↓
🤖 Bot: タイトルを教えてください
   ↓
👤 ユーザー: 「私の人生物語」
   ↓
🤖 Bot: カバー写真を送ってください
   ↓
👤 ユーザー: [カバー写真送信]
   ↓
🤖 Bot: カバー写真を受け取りました！
     表紙PDFを生成中です...⏳
   ↓ (3〜5秒)
🤖 Bot: [Flex Message]
     ✨ 自分史完成！
     📄 PDFを見る（表紙のみ）
     ✏️ 内容を編集
   ↓
🤖 Bot: 📸 次に、見開きページ用の写真を送ってください。
     （例：思い出の風景、大切な瞬間など、縦長の写真推奨）
   ↓
👤 ユーザー: [見開き用写真送信]
   ↓
🤖 Bot: 見開きページ用の写真を受け取りました！📸
     
     最後に、単一ページ用の写真を送ってください。
     （例：思い出の1枚、学生時代の写真など）
   ↓
👤 ユーザー: [単一ページ用写真送信]
   ↓
🤖 Bot: 単一ページ用の写真を受け取りました！
     完全版PDFを生成中です...⏳
   ↓ (3〜5秒)
🤖 Bot: ✨ 完全版の自分史が完成しました！
     
     📄 PDF: [URL]
     ファイル名: memoir_vertical_私の人生物語_20251025.pdf
     サイズ: 1,234,567 bytes
     
     表紙、見開きページ、単一ページの3種類のページを含む、
     本格的な自分史PDFです。
```

## 📊 特徴

### 2段階のPDF生成

1. **第1段階: 表紙のみのPDF（簡易版）**
   - タイトル + カバー写真
   - 3〜5秒で即座に生成
   - ユーザーに早期フィードバック

2. **第2段階: 完全版PDF（メディアテンプレート）**
   - 表紙 + 見開きページ + 単一ページ
   - 3種類のページ型を統合
   - 本格的な自分史レイアウト

### メリット

✅ **早期フィードバック**: 表紙PDFを先に見せることで、ユーザーの離脱を防ぐ
✅ **段階的な情報収集**: 一度に多くを求めず、順番に収集
✅ **高品質な完成品**: メディアテンプレート形式で美しいレイアウト
✅ **柔軟性**: 表紙だけで終わることも、完全版まで進むことも可能

## 🏗️ 技術実装

### データ構造

#### QuickMemoirSession（拡張版）

```python
@dataclass
class QuickMemoirSession:
    session_id: str
    user_id: str
    state: str  # 拡張された状態管理
    data: QuickMemoirData
    spread_image_url: Optional[str] = None  # 見開き画像URL
    single_image_url: Optional[str] = None  # 単一ページ画像URL
    created_at: datetime
    updated_at: datetime
```

#### 状態遷移

```
"waiting_title"          # タイトル入力待ち
   ↓
"waiting_cover"          # カバー写真待ち
   ↓
"waiting_spread_image"   # 見開き画像待ち（新規）
   ↓
"waiting_single_image"   # 単一ページ画像待ち（新規）
   ↓
"editing"                # 編集可能状態
   ↓
"completed"              # 完了
```

### PDF生成メソッド

#### generate_quick_pdf() - 拡張版

```python
async def generate_quick_pdf(
    self, 
    session: QuickMemoirSession,
    vivliostyle_options: Dict[str, Any] = None,
    full_version: bool = False  # 新規パラメータ
) -> Dict[str, Any]:
    """
    PDFを生成
    
    Args:
        full_version: True=完全版（メディアテンプレート）
                     False=表紙のみ（簡易版）
    """
    if full_version and session.spread_image_url and session.single_image_url:
        # 完全版: メディアテンプレート形式
        template_data = self._prepare_media_template_data(session)
        await vivliostyle_service.generate_pdf(
            template_name="media/memoir-vertical",
            data=template_data,
            ...
        )
    else:
        # 表紙のみ: 簡易版
        template_data = self._prepare_template_data(session.data)
        await vivliostyle_service.generate_pdf(
            template_name="memoir",
            data=template_data,
            ...
        )
```

### メディアテンプレートデータ生成

```python
def _prepare_media_template_data(self, session: QuickMemoirSession) -> Dict[str, Any]:
    """メディアテンプレート用にデータを整形（完全版）"""
    return {
        "title": session.data.title,
        "pages": [
            # ページ1: タイトルページ（表紙）
            {
                "page_type": "title",
                "page_number": 1,
                "data": {
                    "title": session.data.title,
                    "author": session.data.author,
                    "cover_image": session.data.cover_image_url
                }
            },
            # ページ2-3: 見開き画像+縦書きテキスト
            {
                "page_type": "spread_image_text",
                "page_number": 2,
                "data": {
                    "image": session.spread_image_url,
                    "story_title": "思い出のひととき",
                    "story_text": "（デフォルトのストーリー文）"
                }
            },
            # ページ4: 単一ページ画像+テキスト
            {
                "page_type": "single_image_text",
                "page_number": 4,
                "data": {
                    "image": session.single_image_url,
                    "section_title": "大切な一枚",
                    "description": "（デフォルトの説明文）"
                }
            }
        ]
    }
```

## 📋 LINEハンドラー統合

### 画像メッセージハンドラー

```python
# カバー写真待ち
if quick_session and quick_session.state == "waiting_cover":
    success, response = quick_memoir_service.process_cover_image(quick_session, file_url)
    send_text_message(response)
    
    # 表紙PDF生成（非同期）
    def generate_cover_pdf():
        pdf_result = quick_memoir_service.generate_quick_pdf(
            quick_session, 
            full_version=False  # 表紙のみ
        )
        # Flex Message送信
        send_memoir_complete_message(pdf_url, edit_url)
        # 続けて見開き画像を依頼
        send_push_message("📸 次に、見開きページ用の写真を送ってください。")
    
    threading.Thread(target=generate_cover_pdf).start()

# 見開き画像待ち
if quick_session and quick_session.state == "waiting_spread_image":
    success, response = quick_memoir_service.process_spread_image(quick_session, file_url)
    send_text_message(response)

# 単一ページ画像待ち
if quick_session and quick_session.state == "waiting_single_image":
    success, response = quick_memoir_service.process_single_image(quick_session, file_url)
    send_text_message(response)
    
    # 完全版PDF生成（非同期）
    def generate_full_pdf():
        pdf_result = quick_memoir_service.generate_quick_pdf(
            quick_session, 
            full_version=True  # 完全版
        )
        send_push_message(f"✨ 完全版の自分史が完成しました！\n📄 {pdf_url}")
    
    threading.Thread(target=generate_full_pdf).start()
```

## 📄 生成されるPDF

### 表紙のみPDF（第1段階）

- **ファイル名**: `memoir_私の人生物語_20251025.pdf`
- **ページ数**: 1ページ
- **内容**: タイトル + 著者名 + カバー画像
- **テンプレート**: `memoir/template.html`

### 完全版PDF（第2段階）

- **ファイル名**: `memoir_vertical_私の人生物語_20251025.pdf`
- **ページ数**: 4ページ
- **内容**: 
  - ページ1: 表紙
  - ページ2-3: 見開き（左: 画像フル、右: 縦書き3段組み）
  - ページ4: 単一ページ（画像+縦書きテキスト）
- **テンプレート**: `media/memoir-vertical/template.html`

## 🎨 デフォルトテキスト

見開きページと単一ページには、ユーザーがテキストを入力していない場合でも、デフォルトの文章が自動挿入されます。

### 見開きページ

**ストーリータイトル**: 「思い出のひととき」

**ストーリー本文**:
```
この写真には、大切な思い出が詰まっています。時が経つにつれて、記憶は少しずつ色褪せていくかもしれません。
しかし、この一枚の写真が、あの日の感動や喜びを鮮やかに蘇らせてくれます。
人生の旅路において、このような瞬間を大切に残しておくことは、とても意味のあることです。
写真を見るたびに、当時の気持ちや周囲の雰囲気が心に蘇ってきます。
それは単なる記録ではなく、心の財産として、これからも大切に保管していきたいと思います。
```

### 単一ページ

**セクションタイトル**: 「大切な一枚」

**説明文**:
```
この写真は、人生の中で特別な意味を持つ一枚です。
何気ない日常の中にも、かけがえのない瞬間が隠れています。
写真として残すことで、その瞬間は永遠に私たちの心に刻まれます。
```

## 🚀 今後の拡張

### Phase 2: テキストのカスタマイズ

ユーザーが見開きページや単一ページのテキストを編集できるようにする：
- 編集画面（LIFF）でテキスト入力フィールドを追加
- AI文章生成機能の統合

### Phase 3: ページの追加

ユーザーが見開きページや単一ページを追加できるようにする：
- 「もう1ページ追加」ボタン
- 動的なページ生成

### Phase 4: テンプレート選択

複数のメディアテンプレートから選択：
- 自分史_縦書き（現在）
- 自分史_横書き
- 旅ログ_横書き
- 推しログ_縦書き

## 🎯 UX設計の意図

### 早期フィードバックの重要性

ユーザーが「作る」と入力してから最初のPDFを受け取るまでの時間を最小化することで：
- ✅ 離脱率の低減
- ✅ 達成感の提供
- ✅ 次のステップへの動機付け

### 段階的な情報収集

一度に多くの情報を求めず、段階的に収集することで：
- ✅ 心理的ハードルの軽減
- ✅ 各ステップでの明確なゴール
- ✅ 途中離脱しても表紙PDFは完成

### メディアテンプレートの活用

構造化されたページ型を使用することで：
- ✅ デザイン性の高いPDF
- ✅ 一貫性のあるレイアウト
- ✅ 拡張性（新しいページ型の追加）

## 📊 メトリクス

### 追跡する指標

- **第1段階完了率**: カバー写真 → 表紙PDF生成
- **第2段階完了率**: 表紙PDF生成 → 完全版PDF生成
- **平均時間**: 各ステップの所要時間
- **離脱ポイント**: どのステップで離脱するか

## 🐛 トラブルシューティング

### 表紙PDFは生成されたが、完全版が生成されない

- `session.spread_image_url` と `session.single_image_url` が正しく保存されているか確認
- `full_version=True` が正しく渡されているか確認

### Flex Messageの後、メッセージが届かない

- `send_push_message()` が正しく呼び出されているか確認
- スレッドが正しく開始されているか確認

### 完全版PDFのレイアウトが崩れている

- `templates/media/memoir-vertical/template.html` を確認
- 画像URLが正しく渡されているか確認
- Vivliostyleのログを確認

## 📚 関連ドキュメント

- [簡易フロー実装ガイド](./quick-flow-guide.md) - 従来の簡易フロー
- [メディアテンプレートガイド](./media-template-guide.md) - メディアテンプレートの詳細
- [設計ドキュメント](./design.md) - 全体設計

## 🎊 まとめ

拡張版簡易フローは、ユーザーに早期フィードバックを提供しながら、段階的に情報を収集し、最終的に高品質な自分史PDFを生成する新しいアプローチです。

**フローのポイント**:
1. タイトル + カバー写真で即座に表紙PDF生成
2. Flex Messageで達成感を提供
3. 見開き画像 → 単一ページ画像を順次収集
4. 完全版PDFを生成（メディアテンプレート形式）

これにより、ユーザーは途中で離脱しても表紙PDFを手に入れることができ、最後まで進めば本格的な自分史を完成させることができます。✨

