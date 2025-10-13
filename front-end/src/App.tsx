// import React from 'react';
import { Sidebar } from './components/Sidebar';
import { ChatArea } from './components/ChatArea';
import { ChatInput } from './components/ChatInput';
import { Modal } from './components/Modal'; // <-- Import Modal
import { useChatbot } from './hooks/useChatbot';
import { useModal } from './hooks/useModal'; // <-- Import useModal

function App() {
  const {
    chats,
    activeChat,
    currentChat,
    isTyping,
    sendMessage,
    selectChat,
    startNewChat,
    deleteChat,
    renameChat,
  } = useChatbot();

  const { isOpen, showModal, hideModal, modalContent } = useModal(); 

  return (
    <> {}
      <div className="h-screen bg-gray-100 flex">
        <Sidebar 
          chats={chats}
          activeChat={activeChat}
          onChatSelect={selectChat}
          onNewChat={startNewChat}
          onDeleteChat={(chatId) => showModal({ 
            title: "Delete Chat",
            children: "Are you sure you want to delete this chat? This action cannot be undone.",
            confirmText: "Delete",
            onConfirm: () => deleteChat(chatId)
          })}
          onRenameChat={(chatId, currentTitle) => showModal({ 
            title: "Rename Chat",
            children: "Enter a new name for this chat.",
            showInput: true,
            initialInputValue: currentTitle,
            confirmText: "Rename",
            onConfirm: (newTitle) => renameChat(chatId, newTitle || '')
          })}
        />
        
        <div className="flex-1 flex flex-col">
          <ChatArea 
            messages={currentChat?.messages || []} 
            isTyping={isTyping}
          />
          
          <ChatInput 
            onSendMessage={sendMessage}
            disabled={isTyping}
          />
        </div>
      </div>
      
      {}
      <Modal 
        isOpen={isOpen}
        onClose={hideModal}
        {...modalContent}
      />
    </>
  );
}

export default App;