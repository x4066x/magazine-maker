import React from 'react'
import ChatInterface from './components/Chat/ChatInterface'
import { ChatProvider } from './components/Chat/ChatContext'

const App: React.FC = () => {
  return (
    <ChatProvider>
      <div className="w-full h-full flex flex-col bg-gray-100">
        <header className="w-full bg-blue-600 text-white p-4 shadow-md">
          <div className="max-w-5xl mx-auto">
            <h1 className="text-2xl font-bold">マガジンメーカー</h1>
          </div>
        </header>
        <main className="flex-1 w-full p-4">
          <div className="max-w-5xl mx-auto h-[calc(100vh-8rem)]">
            <div className="w-full h-full bg-white rounded-lg shadow-lg overflow-hidden">
              <ChatInterface />
            </div>
          </div>
        </main>
      </div>
    </ChatProvider>
  )
}

export default App
