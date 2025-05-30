import OpenAI from 'openai';
import type { Message } from '../../types/chat';

const openai = new OpenAI({
  apiKey: import.meta.env.VITE_OPENAI_API_KEY,
  dangerouslyAllowBrowser: true
});

export const sendMessage = async (messages: Message[]): Promise<Message> => {
  try {
    const response = await openai.chat.completions.create({
      model: "gpt-3.5-turbo",
      messages: messages.map(msg => ({
        role: msg.role,
        content: msg.content
      })),
    });

    return {
      id: Date.now().toString(),
      role: 'assistant',
      content: response.choices[0].message.content || '申し訳ありません。応答を生成できませんでした。',
      timestamp: new Date()
    };
  } catch (error) {
    console.error('OpenAI API Error:', error);
    throw new Error('メッセージの送信中にエラーが発生しました。');
  }
}; 