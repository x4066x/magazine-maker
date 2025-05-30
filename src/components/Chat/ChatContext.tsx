import React, { createContext, useContext, useReducer, useCallback } from 'react';
import type { ReactNode } from 'react';
import type { ChatState, ChatContextType, Message } from '../../types/chat';
import { sendMessage as sendOpenAIMessage } from '../../services/llm/openai';

const initialState: ChatState = {
  messages: [],
  isLoading: false,
  error: null,
};

type ChatAction =
  | { type: 'SEND_MESSAGE_START' }
  | { type: 'SEND_MESSAGE_SUCCESS'; payload: Message }
  | { type: 'SEND_MESSAGE_ERROR'; payload: string }
  | { type: 'CLEAR_MESSAGES' };

const chatReducer = (state: ChatState, action: ChatAction): ChatState => {
  switch (action.type) {
    case 'SEND_MESSAGE_START':
      return { ...state, isLoading: true, error: null };
    case 'SEND_MESSAGE_SUCCESS':
      return {
        ...state,
        messages: [...state.messages, action.payload],
        isLoading: false,
      };
    case 'SEND_MESSAGE_ERROR':
      return { ...state, isLoading: false, error: action.payload };
    case 'CLEAR_MESSAGES':
      return { ...state, messages: [] };
    default:
      return state;
  }
};

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(chatReducer, initialState);

  const sendMessage = useCallback(async (content: string) => {
    try {
      dispatch({ type: 'SEND_MESSAGE_START' });
      
      const userMessage: Message = {
        id: Date.now().toString(),
        role: 'user',
        content,
        timestamp: new Date(),
      };
      
      dispatch({ type: 'SEND_MESSAGE_SUCCESS', payload: userMessage });
      
      const currentMessages = [...state.messages, userMessage];
      console.log('Sending messages to OpenAI:', currentMessages);
      
      const response = await sendOpenAIMessage(currentMessages);
      console.log('Received response from OpenAI:', response);
      
      dispatch({ type: 'SEND_MESSAGE_SUCCESS', payload: response });
    } catch (error) {
      console.error('Chat Error:', error);
      dispatch({ type: 'SEND_MESSAGE_ERROR', payload: 'メッセージの送信に失敗しました' });
    }
  }, [state.messages]);

  const clearMessages = useCallback(() => {
    dispatch({ type: 'CLEAR_MESSAGES' });
  }, []);

  return (
    <ChatContext.Provider value={{ state, sendMessage, clearMessages }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
}; 