import { useState, useCallback, useEffect } from 'react';
import axios from 'axios';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: string;
}

interface Chat {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: string;
  messages: Message[];
}

// The URL for your Python backend server
// Use environment variable for production, fallback to localhost for development
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/chat';

const formatTime = (date: Date): string => {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const generateChatTitle = (message: string): string => {
  const words = message.split(' ').slice(0, 4);
  return words.length < message.split(' ').length
    ? `${words.join(' ')}...`
    : words.join(' ');
};

export const useChatbot = () => {
  // --- RE-ADD LOCALSTORAGE ---
  const [chats, setChats] = useState<Chat[]>(() => {
    try {
      const savedChats = window.localStorage.getItem('chatHistory');
      return savedChats ? JSON.parse(savedChats) : [];
    } catch (error) {
      console.error("Failed to parse chats from localStorage", error);
      return [];
    }
  });

  const [activeChat, setActiveChat] = useState<string>(() => {
    try {
      const savedChats = window.localStorage.getItem('chatHistory');
      if (savedChats) {
        const parsedChats = JSON.parse(savedChats);
        return parsedChats.length > 0 ? parsedChats[0].id : '';
      }
      return '';
    } catch (error) {
      console.error("Failed to parse activeChat from localStorage", error);
      return '';
    }
  });
  
  const [isTyping, setIsTyping] = useState(false);

  // --- RE-ADD USEEFFECT TO SAVE CHATS ---
  useEffect(() => {
    // Only save if chats array is not empty to avoid overwriting on first load
    if (chats.length > 0) {
        window.localStorage.setItem('chatHistory', JSON.stringify(chats));
    }
  }, [chats]);

  const getCurrentChat = useCallback((): Chat | undefined => {
    return chats.find(chat => chat.id === activeChat);
  }, [chats, activeChat]);

  const createNewChat = useCallback((): string => {
    const newChatId = `chat-${Date.now()}`;
    const newChat: Chat = {
      id: newChatId,
      title: 'New Conversation',
      lastMessage: '',
      timestamp: formatTime(new Date()),
      messages: []
    };
    
    setChats(prev => [newChat, ...prev]);
    setActiveChat(newChatId);
    return newChatId;
  }, []);

  const sendMessage = useCallback(async (text: string) => {
    // This function remains the same as the previous version
    if (!text.trim()) return;

    let chatId = activeChat;
    if (!chatId) {
      chatId = createNewChat();
    }

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      text,
      sender: 'user',
      timestamp: formatTime(new Date())
    };

    setChats(prevChats => prevChats.map(chat =>
      chat.id === chatId
        ? {
            ...chat,
            messages: [...chat.messages, userMessage],
            lastMessage: text,
            timestamp: userMessage.timestamp,
            title: chat.title === 'New Conversation' ? generateChatTitle(text) : chat.title
          }
        : chat
    ));

    setIsTyping(true);

    try {
      const response = await axios.post(API_URL, { message: text });
      const botResponseText = response.data.message;

      const botResponse: Message = {
        id: `msg-${Date.now()}-bot`,
        text: botResponseText || "Sorry, I couldn't get a response.",
        sender: 'bot',
        timestamp: formatTime(new Date())
      };

      setChats(prevChats => prevChats.map(chat =>
        chat.id === chatId
          ? {
              ...chat,
              messages: [...chat.messages, botResponse],
              lastMessage: botResponse.text,
              timestamp: botResponse.timestamp
            }
          : chat
      ));

    } catch (error) {
      console.error('Error fetching response from backend:', error);
      const errorResponse: Message = {
        id: `msg-${Date.now()}-bot`,
        text: "Sorry, I'm having trouble connecting to the server.",
        sender: 'bot',
        timestamp: formatTime(new Date())
      };
      setChats(prevChats => prevChats.map(chat =>
        chat.id === chatId
          ? {
              ...chat,
              messages: [...chat.messages, errorResponse],
              lastMessage: errorResponse.text,
              timestamp: errorResponse.timestamp
            }
          : chat
      ));
    } finally {
      setIsTyping(false);
    }
  }, [activeChat, createNewChat]);

  const selectChat = useCallback((chatId: string) => {
    setActiveChat(chatId);
  }, []);

  const startNewChat = useCallback(() => {
    createNewChat();
  }, [createNewChat]);

  const deleteChat = useCallback((chatIdToDelete: string) => {
    setChats(prevChats => {
      const newChats = prevChats.filter(chat => chat.id !== chatIdToDelete);
      if (activeChat === chatIdToDelete) {
        setActiveChat(newChats.length > 0 ? newChats[0].id : '');
      }
      return newChats;
    });
  }, [activeChat]);

  const renameChat = useCallback((chatIdToRename: string, newTitle: string) => {
    if (!newTitle.trim()) return;
    setChats(prevChats =>
      prevChats.map(chat =>
        chat.id === chatIdToRename ? { ...chat, title: newTitle.trim() } : chat
      )
    );
  }, []);

  return {
    chats,
    activeChat,
    currentChat: getCurrentChat(),
    isTyping,
    sendMessage,
    selectChat,
    startNewChat,
    deleteChat,
    renameChat,
  };
};