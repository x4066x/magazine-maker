# LINE Bot 自分史作成サービス - ドキュメント

このディレクトリには、LINE Bot自分史作成サービスの全ドキュメントが含まれています。

---

## 📚 ドキュメント一覧

### 🎯 設計・要求定義

#### [design.md](./design.md)
**LINE Bot 自分史作成サービス - 全体設計** （参考用・一部古い情報あり）

- サービス全体の設計思想
- データ構造
- 技術スタック

**対象読者**: 開発者、プロダクトマネージャー  
**内容**: サービス全体の設計、要求定義、技術スタック

**注意**: このドキュメントには古い情報が含まれています。最新の実装内容は以下のドキュメントを参照してください：
- 拡張版簡易フロー: `extended-quick-flow-guide.md`
- メディアテンプレート: `media-template-guide.md`

---

### 🚀 実装ガイド

#### [extended-quick-flow-guide.md](./extended-quick-flow-guide.md) ⭐**最新**
**拡張版簡易フロー - 実装ガイド**

- 2段階PDF生成フロー（表紙のみ → 完全版）
- メディアテンプレート統合
- 技術実装の詳細
- データ構造とフロー
- UX設計の意図

**対象読者**: 開発者  
**内容**: 最新の簡易フロー実装（タイトル→カバー→表紙PDF→見開き画像→単一ページ画像→完全版PDF）

**推奨**: これが最新の実装ガイドです。まずこれを読んでください。

---

#### [media-template-guide.md](./media-template-guide.md) ⭐**最新**
**メディアテンプレート - 実装ガイド**

- メディアテンプレートの概念とスキーマ
- `memoir_vertical` (自分史_縦書き) テンプレート
- ページ型の定義と拡張方法
- 編集画面の実装
- 新しいテンプレートの追加方法

**対象読者**: 開発者  
**内容**: メディアテンプレートシステムの全体像と実装詳細

---

#### [quick-flow-guide.md](./quick-flow-guide.md) （参考用）
**旧・簡易自分史作成フロー - 実装ガイド**

写真フローなど、一部実装されていない機能の設計が含まれています。最新の実装は `extended-quick-flow-guide.md` を参照してください。

---

#### [vivliostyle-integration.md](./vivliostyle-integration.md)
**Vivliostyle PDF生成 統合ガイド**

- Auto-DesignerからVivliostyleへの移行理由
- 変更内容
- テンプレート構成
- 使い方
- **⚡ 2025-10-25更新**: 画像処理の最適化
  - ローカルメディアファイルの高速処理
  - HTTPダウンロードからファイルコピーへ
  - 10倍のパフォーマンス向上
- 技術詳細
- メリット
- テスト方法

**対象読者**: 開発者  
**内容**: Vivliostyle統合の実装詳細、データフロー、ファイル構造

---

#### [vivliostyle-options.md](./vivliostyle-options.md)
**Vivliostyle オプション設定ガイド**

- 利用可能なオプション
  - 基本オプション（format, size, single_doc, timeout）
  - 印刷用オプション（crop_marks, bleed）
  - 高度なオプション（css）
- 使い方（コード例）
- 用紙サイズ一覧
- 印刷用設定例
- カスタムCSS例
- タイムアウト設定の目安

**対象読者**: 開発者、デザイナー  
**内容**: Vivliostyle CLIオプションの使用方法、カスタマイズ方法

---

### 🔧 トラブルシューティング

#### [troubleshooting-vivliostyle.md](./troubleshooting-vivliostyle.md)
**Vivliostyle PDF生成 トラブルシューティング**

- 作業履歴
- **⚡ 2025-10-25追加**: 問題0: 画像処理がタイムアウトする（最重要）
  - HTTPダウンロードタイムアウトの原因と解決策
  - ローカルファイル直接コピーへの改善
  - パフォーマンス比較（30秒→3秒）
- 発生した問題と解決策
  - 問題1: PDFファイルが生成されない
  - 問題2: 画像URLが処理されない
  - 問題3: デバッグ情報が不足
  - 問題4: サーバー再起動しないと反映されない
- チェックリスト
- ベストプラクティス
- 今後の改善案

**対象読者**: 開発者、運用担当者  
**内容**: 実際に発生した問題と解決策、デバッグ方法、ベストプラクティス

**最重要**: 画像処理のタイムアウト問題が解決され、10倍以上高速化しました（問題0を参照）

---

## 🗺️ ドキュメント構成図

```
docs/
├── README.md (このファイル)
├── extended-quick-flow-guide.md ⭐ (拡張版簡易フロー - 最新)
├── media-template-guide.md ⭐ (メディアテンプレート - 最新)
├── vivliostyle-integration.md (Vivliostyle統合ガイド)
├── vivliostyle-options.md (Vivliostyleオプション設定)
├── troubleshooting-vivliostyle.md (トラブルシューティング)
├── design.md (全体設計 - 参考用)
└── quick-flow-guide.md (旧・簡易フロー - 参考用)
```

---

## 📖 読む順序（推奨）

### 新規メンバー向け

1. **[extended-quick-flow-guide.md](./extended-quick-flow-guide.md)** ⭐ - 最新の簡易フローを理解
2. **[media-template-guide.md](./media-template-guide.md)** ⭐ - メディアテンプレートシステムを理解
3. **[vivliostyle-integration.md](./vivliostyle-integration.md)** - PDF生成の仕組みを理解
4. **[vivliostyle-options.md](./vivliostyle-options.md)** - オプションの使い方を学ぶ

### トラブル発生時

1. **[troubleshooting-vivliostyle.md](./troubleshooting-vivliostyle.md)** - 既知の問題と解決策を確認
2. 該当するドキュメント（vivliostyle-integration.md など）で詳細を確認

### 新機能追加時

1. **[media-template-guide.md](./media-template-guide.md)** - メディアテンプレートの追加方法を確認
2. **[extended-quick-flow-guide.md](./extended-quick-flow-guide.md)** - フロー統合の方法を確認
3. **[troubleshooting-vivliostyle.md](./troubleshooting-vivliostyle.md)** - ベストプラクティスを確認

---

## 🔍 クイックリンク

### よくある質問

**Q: PDF生成に失敗する**  
→ [troubleshooting-vivliostyle.md - 問題1](./troubleshooting-vivliostyle.md#問題1-pdfファイルが生成されない)

**Q: 用紙サイズを変更したい**  
→ [vivliostyle-options.md - 用紙サイズ一覧](./vivliostyle-options.md#用紙サイズ一覧)

**Q: 印刷用にトンボを追加したい**  
→ [vivliostyle-options.md - 印刷用設定例](./vivliostyle-options.md#印刷用設定例)

**Q: 画像が表示されない**  
→ [troubleshooting-vivliostyle.md - 問題2](./troubleshooting-vivliostyle.md#問題2-画像urlが処理されない)

**Q: タイムアウトエラーが発生する**  
→ [vivliostyle-options.md - タイムアウト設定](./vivliostyle-options.md#タイムアウト設定の目安)

**Q: 最新の簡易フローの仕組みを知りたい**  
→ [extended-quick-flow-guide.md](./extended-quick-flow-guide.md)

**Q: メディアテンプレートとは？**  
→ [media-template-guide.md](./media-template-guide.md)

**Q: 新しいメディアタイプ（旅ログなど）を追加したい**  
→ [media-template-guide.md - 新しいテンプレートの追加方法](./media-template-guide.md#新しいテンプレートの追加方法)

---

## 📝 ドキュメント更新ルール

### 更新が必要な場合

- 新機能を追加した時
- バグを修正した時
- 設計を変更した時
- 新しい問題と解決策を発見した時

### 更新方法

1. 該当するドキュメントを開く
2. 内容を追記・修正
3. 更新履歴に記録（該当する場合）
4. このREADMEも必要に応じて更新

### ドキュメントの品質

- **明確**: 専門用語は説明する
- **具体的**: コード例を含める
- **最新**: 古い情報は削除または更新
- **整理**: 見出しと構造を適切に使う

---

## 🛠️ 技術スタック（参考）

### バックエンド
- **Python 3.9+**: FastAPI
- **LINE Messaging API**: メッセージ送受信
- **OpenAI API**: 文章生成
- **Vivliostyle CLI**: PDF生成

### フロントエンド（編集画面）
- **HTML5 / CSS3 / JavaScript**
- **Tailwind CSS風スタイル**

### テンプレートエンジン
- **Jinja2**: HTMLテンプレート

---

## 📊 プロジェクト構成

```
line-bot/
├── app/
│   ├── api/
│   │   └── routes.py (APIエンドポイント)
│   ├── services/
│   │   ├── quick_memoir_service.py (拡張版簡易フロー)
│   │   ├── media_template_schema.py (メディアテンプレートスキーマ)
│   │   ├── media_memoir_service.py (メディアフロー - 将来的に統合)
│   │   ├── vivliostyle_service.py (PDF生成)
│   │   ├── openai_service.py (LLM文章生成)
│   │   └── line_service.py (LINE連携)
│   ├── config/
│   │   └── settings.py (設定)
│   └── main.py (エントリーポイント)
├── templates/
│   ├── memoir/
│   │   └── template.html (従来の自分史テンプレート)
│   └── media/
│       └── memoir-vertical/
│           └── template.html (メディアテンプレート: 自分史_縦書き)
├── liff/
│   ├── edit.html (従来の編集画面)
│   └── edit-media.html (メディアテンプレート編集画面)
├── docs/ (このディレクトリ)
│   ├── README.md
│   ├── extended-quick-flow-guide.md ⭐
│   ├── media-template-guide.md ⭐
│   ├── vivliostyle-integration.md
│   ├── vivliostyle-options.md
│   ├── troubleshooting-vivliostyle.md
│   ├── design.md (参考用)
│   └── quick-flow-guide.md (参考用)
└── uploads/ (PDF・画像保存先)
```

---

## 🔗 外部リソース

### LINE
- [LINE Developers](https://developers.line.biz/)
- [LINE Messaging API](https://developers.line.biz/ja/docs/messaging-api/)
- [LINE LIFF](https://developers.line.biz/ja/docs/liff/)

### Vivliostyle
- [Vivliostyle 公式サイト](https://vivliostyle.org/)
- [Vivliostyle CLI Documentation](https://docs.vivliostyle.org/#/cli)
- [Vivliostyle Viewer](https://vivliostyle.org/viewer/)

### OpenAI
- [OpenAI Platform](https://platform.openai.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)

### Python
- [FastAPI](https://fastapi.tiangolo.com/)
- [Jinja2](https://jinja.palletsprojects.com/)
- [Requests](https://requests.readthedocs.io/)

---

## 🤝 貢献

ドキュメントの改善提案や新しい問題・解決策の追加は大歓迎です！

1. 該当するドキュメントを編集
2. 分かりやすい説明を追加
3. コード例を含める（可能な場合）
4. このREADMEも更新（必要な場合）

---

## 📞 サポート

質問や問題がある場合：

1. まず該当するドキュメントを確認
2. [troubleshooting-vivliostyle.md](./troubleshooting-vivliostyle.md) でチェックリストを確認
3. それでも解決しない場合は、開発チームに相談

---

**最終更新**: 2025-10-25  
**バージョン**: 2.0.0 - メディアテンプレート対応

## 🎉 最新情報（v2.0.0）

### 拡張版簡易フロー
- タイトル+カバー写真で即座に表紙PDF生成
- 見開き画像、単一ページ画像を追加収集
- 完全版PDF（4ページ）を自動生成

### メディアテンプレート
- スキーマ駆動のテンプレートシステム
- `memoir_vertical`（自分史_縦書き）実装済み
- 将来的に旅ログ、推しログなど追加可能

### 編集機能
- メディアテンプレート専用編集画面
- 見開きページと単一ページのテキスト編集
- AI文章生成機能（将来実装予定）

詳細は [extended-quick-flow-guide.md](./extended-quick-flow-guide.md) と [media-template-guide.md](./media-template-guide.md) を参照してください。

