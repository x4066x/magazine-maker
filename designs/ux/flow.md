1. 「編集を含む入力画面」を用意する 3 通り
方式	概要	開発コスト	UX/再編集	音声入力
A. LIFF（LINE 内 SPA）	LINE の in-app WebView 上で /liffId を開き、liff.sendMessages() でプレビューを返す	低〜中	チャット→編集画面に遷移しても LINE に戻るだけ／24 h 再編集ボタンなど実装しやすい	getUserMedia() 可
※iOS WKWebView では Web Speech API が非対応
MDN Web Docs
。録音→サーバー側で STT が安全
B. 一時 URL（https ページ）	署名付き URL や Cloud Front の /edit?token=… を 30 分〜24 h だけ有効化して送る	低	LINE 内ブラウザで直接開く。LIFF API は使えないので「送信」ボタンは REST 経由	環境は A と同じ
（iOS で Web Speech 不可、Android Chrome 可）
C. 外部ブラウザ強制起動	target="_blank" ＋ Universal Link／LP を案内し Safari/Chrome を開かせる	中	戻る動線を要設計	フルブラウザなので Web Speech･WebRTC が両 OS で動作

元設計（チャット完結 6 ターン / 必須4項目） を壊さず最小構成で済むのは A。だが「あとで細かく直したい」「音声で長文を追記したい」場合は A に 編集用 LIFF を重ねるか、B を発行するのが現実解。

2. モダリティ別フロー案
mermaid
コピーする
編集する
''' markdown
graph TD
  subgraph 0️⃣ 初回チャット
    Q1(氏名) --> Q2(自己紹介)
    Q2 --> Q3(写真アップ)
    Q3 --> Q4(利用許諾)
    Q4 --> P0[📄 プレビュー生成]
  end
  P0 --> |「編集する」| E[編集画面(A or B)]
  E --> P1[📄 更新プレビュー]
  P1 --> ConfirmOK(✅ 確定) --> Done(🎉 完成物 URL 送付)
'''
ステップ	テキスト	画像	音声	API 例
入力	Quick Reply / テキストフォーム	<input type="file" accept="image/*">	🎙️「録音開始」ボタン
→ MediaRecorder でストリームを /upload POST	OpenAI Realtime / Gemini Live へ WS or Streaming で転送
プレビュー	Flex Message / iframe	同上	音声→文字起こし結果を可視化	Whisper / Gemini ASR
確認	OK / 修正	再アップ可	再録音可	同上

マイク実装の落とし穴

LINE の in-app ブラウザは HTTPS であれば getUserMedia() を許可。ただし SpeechRecognition は iOS WKWebView で動かない ため、録音ファイルをサーバーで STT するバックエンド方式が無難
MDN Web Docs
。

Android は Chrome Engine なので Web Speech API がそのまま使える。OS 判定でフロントエンド STT ↔ バックエンド STT を切替えると最適。

3. 推奨シナリオ
チャット完結 MVP（すでに実装済み思考）を軸に

「再編集」ボタンを押すと LIFF v2 SPA が開く

ここで音声・画像・テキストをまとめて編集可

送信後 liff.sendMessages() で最新版プレビューを返送

音声入力は OS に応じて

Android Chrome → SpeechRecognition + コンテキストストリーミング to OpenAI Realtime

iOS → MediaRecorder → back-end Whisper/Gemini LiveAPI で文字起こし

もし LINE 制限を避けたい高度編集（PDF レイアウト確認 など）

編集リンクの「PC で開く」ボタンだけ B (一時 URL) を発行

または C でフルブラウザを推奨

4. コストとロードマップ
Phase 1: 既存チャット 6 ターン + 「編集」LIFF を追加（最小工数）

Phase 2: 音声入力（Android 先行 → iOS 録音バックエンド）

Phase 3: Gemini LiveAPI 連携／リアルタイム生成プレビュー

Phase 4: 外部 URL or PC ダッシュボードで高度レイアウト校正

この順で段階的に拡張すれば、開発コストを抑えつつ UX を崩さず「マルチモーダル編集」が実現できます。