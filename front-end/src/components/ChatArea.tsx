import React, { useEffect, useRef } from 'react';
import { ChatBubble } from './ChatBubble';
import { MessageSquare } from 'lucide-react';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: string;
}

interface ChatAreaProps {
  messages: Message[];
  isTyping?: boolean;
}

export const ChatArea: React.FC<ChatAreaProps> = ({ messages, isTyping = false }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  return (
    <div className="flex-1 overflow-y-auto bg-gray-50 p-6">
      {messages.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-full text-gray-400">
          <MessageSquare className="w-16 h-16 mb-4 opacity-50" />
          <h3 className="text-lg font-medium mb-2">Welcome to PCTE Helpdesk Chatbot</h3>
          <p className="text-center max-w-md">
            Hi! I'm your virtual assistant from PCTE (Punjab College of Technical Education). 
            I'm here to help you with any questions about courses, schedules, campus services, 
            admissions, fees, and more. How can I assist you today?
          </p>
        </div>
      ) : (
        <div className="space-y-1">
          {messages.map((message) => (
            <ChatBubble key={message.id} message={message} />
          ))}
          
          {isTyping && (
            <div className="flex items-end space-x-2 mb-4">
              <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center flex-shrink-0">
                <MessageSquare className="w-4 h-4 text-gray-600" />
              </div>
              
              <div className="bg-gray-100 px-4 py-3 rounded-2xl rounded-bl-sm">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      )}
    </div>
  );
};