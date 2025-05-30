import React from 'react';
import { useChat } from './ChatContext';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

const ChatInterface: React.FC = () => {
  const { state, sendMessage } = useChat();
  const { messages, isLoading, error } = state;

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4">
        <MessageList messages={messages} />
      </div>
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <span className="block sm:inline">{error}</span>
        </div>
      )}
      <div className="border-t p-4">
        <MessageInput onSendMessage={sendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
};

export default ChatInterface; 