# マガジンメーカー 設計ドキュメント

## 1. システム概要
LLMとの対話を通じてコンテンツを収集し、paged.jsを使用してPDFを生成するWebアプリケーション

## 2. 技術スタック
- フロントエンド: React + TypeScript
- PDF生成: paged.js
- LLM API: OpenAI API
- スタイリング: Tailwind CSS
- ビルドツール: Vite

## 3. ディレクトリ構造
```
src/
├── components/
│   ├── Chat/
│   │   ├── ChatInterface.tsx
│   │   ├── MessageList.tsx
│   │   └── MessageInput.tsx
│   ├── PDF/
│   │   ├── PDFPreview.tsx
│   │   └── PDFGenerator.tsx
│   └── Layout/
│       └── MainLayout.tsx
├── services/
│   ├── llm/
│   │   └── openai.ts
│   └── pdf/
│       └── pagedService.ts
├── types/
│   ├── chat.ts
│   └── pdf.ts
├── utils/
│   ├── chatHelpers.ts
│   └── pdfHelpers.ts
├── App.tsx
└── main.tsx
```

## 4. 主要コンポーネントの説明

### 4.1 ChatInterface
- LLMとの対話を管理するメインコンポーネント
- メッセージの履歴管理
- ユーザー入力の処理
- LLM APIとの通信

### 4.2 PDFGenerator
- 収集したコンテンツをPDFに変換
- paged.jsを使用したPDF生成
- プレビュー機能
- ダウンロード機能

## 5. データフロー
1. ユーザーがチャットインターフェースでLLMと対話
2. 対話内容をメッセージ履歴として保存
3. 十分な情報が集まったら、コンテンツを整理
4. 整理されたコンテンツをpaged.jsでPDFに変換
5. プレビュー表示とダウンロード機能を提供

## 6. API設計

### 6.1 LLM API
```typescript
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
}

interface ChatContextType {
  state: ChatState;
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
}
```

### 6.2 PDF生成API
```typescript
interface PDFOptions {
  format: 'A4' | 'Letter';
  orientation: 'portrait' | 'landscape';
  margin: number;
}

interface PDFResponse {
  url: string;
  status: 'success' | 'error';
}
```

## 7. 実装手順
1. プロジェクトの初期設定
   - 必要なパッケージのインストール
   - ディレクトリ構造の作成
2. チャットインターフェースの実装
3. LLM APIとの連携
4. PDF生成機能の実装
5. UI/UXの改善
6. エラーハンドリングの実装
7. テストの作成

## 8. 必要なパッケージ
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "pagedjs": "^0.3.0",
    "openai": "^4.0.0",
    "tailwindcss": "^3.3.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0"
  }
}
```

## 9. セキュリティ考慮事項
- APIキーの安全な管理
- ユーザー入力のサニタイズ
- レート制限の実装
- エラーメッセージの適切な処理

## 10. 今後の拡張性
- テンプレート機能の追加
- 複数のLLMプロバイダーのサポート
- カスタムスタイルの適用
- バッチ処理機能
- ユーザー認証の追加

## 11. 現状の実装状況
- プロジェクトの初期設定が完了
  - Vite + React + TypeScript + Tailwind CSSの設定
  - 必要なパッケージのインストール
  - 開発環境の構築
- チャットインターフェースの実装が完了
  - ChatContextによる状態管理
    - メッセージ履歴の管理
    - ローディング状態の管理
    - エラー状態の管理
  - ChatInterfaceコンポーネント
    - メッセージリストの表示
    - 入力フォームの実装
    - エラー表示の実装
  - MessageListコンポーネント
    - ユーザーとアシスタントのメッセージを区別して表示
    - メッセージの配置を役割に応じて調整
    - レスポンシブなレイアウト
  - MessageInputコンポーネント
    - メッセージ入力フォーム
    - 送信ボタン
    - ローディング状態の表示
    - バリデーション
- 開発用モックの実装
  - OpenAI APIの基本実装完了
    - .envファイルからのAPIキー読み込み
    - 基本的なAPI通信機能
  - テスト用のレスポンス
- UIデザインの実装
  - Tailwind CSSによるスタイリング
  - レスポンシブデザイン
  - アクセシビリティ対応
  - ダークモード対応の準備
- 次のステップ
  - OpenAI APIの本番実装
  - PDFプレビュー機能の実装
  - PDFダウンロード機能の実装
  - メッセージ履歴の永続化

## 12. 実装の改善点
- チャット機能の安定性向上
  - メッセージ履歴の適切な管理
  - 型の統一による型安全性の向上
  - エラーハンドリングの強化
  - OpenAI APIのエラーハンドリング改善
  - 関数のメモ化によるパフォーマンス最適化
- デバッグ機能の強化
  - コンソールログの追加
  - エラー情報の詳細化
  - メッセージの送受信の可視化
- コードの保守性向上
  - 型定義の整理
  - コンポーネントの責務の明確化
  - エラーハンドリングの統一
  - 関数の再利用性の向上

## 13. 既知の問題と今後の課題
- OpenAI APIの機能拡張
  - より詳細なエラーハンドリングの実装
  - ストリーミングレスポンスの実装検討
  - プロンプトの最適化
- メッセージ履歴の永続化
  - ローカルストレージの利用
  - データベースの検討
- UIの改善
  - ダークモードの実装
  - アニメーションの追加
  - ローディングインジケータの改善
- PDF機能の実装
  - paged.jsの導入
  - プレビュー機能の実装
  - カスタムテンプレートの作成 