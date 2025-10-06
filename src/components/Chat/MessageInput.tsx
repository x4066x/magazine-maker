import React, { useState } from 'react';
import type { FormEvent } from 'react';

interface MessageInputProps {
  onSendMessage: (content: string) => Promise<void>;
  isLoading: boolean;
}

const MessageInput: React.FC<MessageInputProps> = ({ onSendMessage, isLoading }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;

    const trimmedMessage = message.trim();
    setMessage('');
    await onSendMessage(trimmedMessage);
  };

  return (
    <form onSubmit={handleSubmit} className="w-full flex gap-2">
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="メッセージを入力..."
        disabled={isLoading}
        className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
      />
      <button
        type="submit"
        disabled={isLoading || !message.trim()}
        className={`px-6 py-2 rounded-lg text-white font-medium transition-colors ${
          isLoading || !message.trim()
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-blue-500 hover:bg-blue-600'
        }`}
      >
        {isLoading ? '送信中...' : '送信'}
      </button>
    </form>
  );
};

export default MessageInput; 