import React from 'react'
import './App.css'
import ChatInterface from './components/Chat/ChatInterface'
import { ChatProvider } from './components/Chat/ChatContext'

const App: React.FC = () => {
  return (
    <ChatProvider>
      <div className="h-screen flex flex-col">
        <header className="bg-blue-600 text-white p-4">
          <h1 className="text-2xl font-bold">マガジンメーカー</h1>
        </header>
        <main className="flex-1 p-4">
          <ChatInterface />
        </main>
      </div>
    </ChatProvider>
  )
}

export default App
