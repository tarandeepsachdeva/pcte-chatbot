import React from 'react';
import { Bot, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown'; // <-- 1. IMPORT

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: string;
}

interface ChatBubbleProps {
  message: Message;
}

export const ChatBubble: React.FC<ChatBubbleProps> = ({ message }) => {
  const isUser = message.sender === 'user';
  
  return (
    <div className={`flex items-end space-x-2 mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center flex-shrink-0">
          <Bot className="w-4 h-4 text-gray-600" />
        </div>
      )}
      
      <div className={`max-w-[80vw] sm:max-w-md md:max-w-lg ${isUser ? 'order-1' : 'order-2'}`}>
        <div
          className={`px-4 py-3 rounded-2xl shadow-sm ${
            isUser
              ? 'bg-red-600 text-white rounded-br-sm'
              : 'bg-gray-100 text-gray-900 rounded-bl-sm'
          }`}
        >
          {/* --- 2. USE MARKDOWN FOR BOT MESSAGES --- */}
          {isUser ? (
            <p className="text-sm leading-relaxed">{message.text}</p>
          ) : (
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown>{message.text}</ReactMarkdown>
            </div>
          )}
        </div>
        
        <div className={`mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
          <span className="text-xs text-gray-400">{message.timestamp}</span>
        </div>
      </div>
      
      {isUser && (
        <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0">
          <User className="w-4 h-4 text-red-600" />
        </div>
      )}
    </div>
  );
};