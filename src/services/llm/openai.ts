import OpenAI from 'openai';
import type { ChatMessage } from '../../types/chat';

// Viteの環境変数はimport.meta.envから取得
const apiKey = import.meta.env.VITE_OPENAI_API_KEY;

if (!apiKey) {
  throw new Error('OpenAI APIキーが設定されていません。.envファイルにVITE_OPENAI_API_KEYを設定してください。');
}

const openai = new OpenAI({
  apiKey: apiKey,
  dangerouslyAllowBrowser: true  // ブラウザでの使用を許可
});

export async function sendMessage(content: string, history: ChatMessage[] = []): Promise<ChatMessage> {
  try {
    const messages = [
      ...history.map(msg => ({
        role: msg.role,
        content: msg.content
      })),
      { role: 'user' as const, content }
    ];

    const response = await openai.chat.completions.create({
      model: 'gpt-3.5-turbo',
      messages: messages,
    });

    const assistantMessage = response.choices[0]?.message?.content || '応答を生成できませんでした。';

    return {
      id: Date.now().toString(),
      role: 'assistant',
      content: assistantMessage,
      timestamp: new Date()
    };
  } catch (error) {
    console.error('OpenAI API エラー:', error);
    throw new Error('メッセージの送信中にエラーが発生しました。');
  }
} 