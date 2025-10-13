import React, { useState } from 'react';
import { MessageCircle, Clock, MoreHorizontal, Edit, Trash2 } from 'lucide-react';

interface Chat {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: string;
}

interface SidebarProps {
  chats: Chat[];
  activeChat: string;
  onChatSelect: (chatId: string) => void;
  onNewChat: () => void;
  onDeleteChat: (chatId: string) => void; 
  onRenameChat: (chatId: string, currentTitle: string) => void; 
}

const ChatItem: React.FC<{ chat: Chat } & Omit<SidebarProps, 'chats' | 'onNewChat'>> = ({
  chat,
  activeChat,
  onChatSelect,
  onDeleteChat,
  onRenameChat
}) => {
  const [menuOpen, setMenuOpen] = useState(false);

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDeleteChat(chat.id);
    setMenuOpen(false);
  };

  const handleRename = (e: React.MouseEvent) => {
    e.stopPropagation();
    onRenameChat(chat.id, chat.title); 
    setMenuOpen(false);
  };

  return (
    <div
      onClick={() => onChatSelect(chat.id)}
      className={`p-3 rounded-lg cursor-pointer transition-colors duration-150 relative group ${
        activeChat === chat.id
          ? 'bg-red-50 border border-red-200'
          : 'hover:bg-gray-50'
      }`}
    >
      <div className="flex justify-between items-start">
        <div className="flex-1 overflow-hidden">
          <h3 className="font-medium text-gray-900 text-sm truncate">{chat.title}</h3>
          <p className="text-xs text-gray-500 mt-1 truncate">{chat.lastMessage}</p>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            setMenuOpen(!menuOpen);
          }}
          className="opacity-0 group-hover:opacity-100 focus:opacity-100 p-1 rounded-full hover:bg-gray-200"
        >
          <MoreHorizontal className="w-4 h-4 text-gray-500" />
        </button>
      </div>

      {menuOpen && (
        <div className="absolute top-8 right-2 w-32 bg-white border rounded-md shadow-lg z-10">
          <button onClick={handleRename} className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2">
            <Edit className="w-3 h-3" />
            <span>Rename</span>
          </button>
          <button onClick={handleDelete} className="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center space-x-2">
            <Trash2 className="w-3 h-3" />
            <span>Delete</span>
          </button>
        </div>
      )}
    </div>
  );
};


export const Sidebar: React.FC<SidebarProps> = ({ 
  chats, 
  activeChat, 
  onChatSelect, 
  onNewChat,
  onDeleteChat,
  onRenameChat
}) => {
  return (
    <div className="w-80 bg-white border-r border-gray-200 flex flex-col h-full">
      {}
      <div className="p-6 border-b border-gray-100">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-12 h-12 flex items-center justify-center">
            <img 
              src="/pcte-logo.svg" 
              alt="PCTE Logo" 
              className="w-12 h-12 object-contain"
            />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">PCTE</h1>
            <p className="text-sm text-gray-500">Helpdesk Chatbot</p>
          </div>
        </div>
        <button
          onClick={onNewChat}
          className="w-full bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-2"
        >
          <MessageCircle className="w-4 h-4" />
          <span>New Chat</span>
        </button>
      </div>

      {}
      <div className="flex-1 overflow-y-auto">
        <div className="p-4">
          <h2 className="text-sm font-semibold text-gray-600 mb-3 flex items-center">
            <Clock className="w-4 h-4 mr-2" />
            Chat History
          </h2>
          
          {chats.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              <MessageCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No previous chats</p>
            </div>
          ) : (
            <div className="space-y-2">
              {chats.map((chat) => (
                <ChatItem
                  key={chat.id}
                  chat={chat}
                  activeChat={activeChat}
                  onChatSelect={onChatSelect}
                  onDeleteChat={onDeleteChat}
                  onRenameChat={onRenameChat}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};