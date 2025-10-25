# LINE Bot 自分史作成サービス - ドキュメント

このディレクトリには、LINE Bot自分史作成サービスの全ドキュメントが含まれています。

---

## 📚 ドキュメント一覧

### 🎯 設計・要求定義

#### [design.md](./design.md)
**LINE Bot 自分史作成サービス - 簡易フロー設計**

- 目的と課題
- 新しいチャットフロー
- 初期PDF生成の仕様
- LIFF編集画面の仕様
- LLM文章生成機能
- API設計
- データ構造
- 実装フェーズ
- **🚨 NEW**: 現在のフォームベース編集の課題
- **💡 NEW**: 写真中心・対話ベース自分史アプローチ
- **⚡ 2025-10-25更新**: パフォーマンスとUX改善
  - イベントループ問題の修正
  - 画像処理の最適化（30秒→3秒）
  - セッション管理の改善
  - Flex Messageデザイン更新

**対象読者**: 開発者、プロダクトマネージャー  
**内容**: サービス全体の設計、要求定義、技術スタック

**重要**: 
- 現在のフォームベース編集には課題があり、新しい「写真中心・対話ベース」アプローチを設計しました
- 最新の技術改善により、PDF生成が10倍高速化し、安定性が向上しました
- 詳細は design.md の各セクションを参照してください

---

### 🚀 実装ガイド

#### [quick-flow-guide.md](./quick-flow-guide.md)
**簡易自分史作成フロー - 実装ガイド**

- 実装完了した作業（現在のフォームベース編集）
- **⚡ NEW**: 技術的な特徴
  - 高速な画像処理（3秒以内）
  - 非同期処理の最適化
  - Single Source of Truth原則のセッション管理
- 新しいフローの特徴
- 使い方
- 実装プラン
- 主な機能
- **🚨 NEW**: 現在のフローの課題
- **💡 NEW**: 写真中心・対話ベース自分史の実装ガイド

**対象読者**: 開発者  
**内容**: 簡易フロー機能の実装手順、ファイル構成、テスト方法

**最新アップデート**: PDF生成が劇的に高速化し、安定性が向上しました（2025-10-25）

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
├── design.md (設計・要求定義)
├── quick-flow-guide.md (簡易フロー実装ガイド)
├── vivliostyle-integration.md (Vivliostyle統合ガイド)
├── vivliostyle-options.md (Vivliostyleオプション設定)
└── troubleshooting-vivliostyle.md (トラブルシューティング)
```

---

## 📖 読む順序（推奨）

### 新規メンバー向け

1. **[design.md](./design.md)** - 全体の設計を理解
2. **[quick-flow-guide.md](./quick-flow-guide.md)** - 簡易フローの実装を理解
3. **[vivliostyle-integration.md](./vivliostyle-integration.md)** - PDF生成の仕組みを理解
4. **[vivliostyle-options.md](./vivliostyle-options.md)** - オプションの使い方を学ぶ

### トラブル発生時

1. **[troubleshooting-vivliostyle.md](./troubleshooting-vivliostyle.md)** - 既知の問題と解決策を確認
2. 該当するドキュメント（vivliostyle-integration.md など）で詳細を確認

### 新機能追加時

1. **[design.md](./design.md)** - 設計方針を確認
2. 該当する実装ガイドを参照
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

**Q: 簡易フローの仕組みを知りたい**  
→ [quick-flow-guide.md](./quick-flow-guide.md)

**Q: LLM文章生成機能の使い方**  
→ [design.md - LLM文章生成機能](./design.md#llm文章生成機能)

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
│   │   ├── quick_memoir_service.py (簡易フロー)
│   │   ├── vivliostyle_service.py (PDF生成)
│   │   ├── openai_service.py (LLM文章生成)
│   │   └── line_service.py (LINE連携)
│   ├── config/
│   │   └── settings.py (設定)
│   └── main.py (エントリーポイント)
├── templates/
│   └── memoir/
│       └── template.html (自分史テンプレート)
├── liff/
│   └── edit.html (編集画面)
├── docs/ (このディレクトリ)
│   ├── README.md
│   ├── design.md
│   ├── quick-flow-guide.md
│   ├── vivliostyle-integration.md
│   ├── vivliostyle-options.md
│   └── troubleshooting-vivliostyle.md
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
**バージョン**: 1.0.0

