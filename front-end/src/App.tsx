import { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { ChatArea } from './components/ChatArea';
import { ChatInput } from './components/ChatInput';
import { Modal } from './components/Modal'; // <-- Import Modal
import { useChatbot } from './hooks/useChatbot';
import { useModal } from './hooks/useModal'; // <-- Import useModal
import { Menu } from 'lucide-react';

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
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      <div className="h-screen bg-gray-100 flex flex-col md:flex-row">
        {/* Mobile header */}
        <div className="md:hidden bg-white border-b border-gray-200">
          <div className="flex items-center justify-between p-4">
            <button
              onClick={() => setMobileOpen(true)}
              className="p-2 rounded-md hover:bg-gray-100"
              aria-label="Open menu"
            >
              <Menu className="w-6 h-6" />
            </button>
            <div className="flex items-center space-x-3">
              <img src="/pcte-logo.svg" alt="PCTE Logo" className="w-8 h-8 object-contain" />
              <div>
                <h1 className="text-base font-bold text-gray-900 leading-tight">PCTE</h1>
                <p className="text-xs text-gray-500 -mt-0.5">Helpdesk Chatbot</p>
              </div>
            </div>
            <div className="w-10" />
          </div>
        </div>

        {/* Desktop sidebar */}
        <div className="hidden md:block">
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
        </div>
        
        {/* Main content */}
        <div className="flex-1 flex flex-col min-h-0">
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

      {/* Mobile sidebar overlay */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 flex md:hidden">
          <div className="h-full w-4/5 max-w-xs bg-white shadow-xl">
            <Sidebar 
              chats={chats}
              activeChat={activeChat}
              onChatSelect={(id) => { selectChat(id); setMobileOpen(false); }}
              onNewChat={() => { startNewChat(); setMobileOpen(false); }}
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
          </div>
          <div className="flex-1 bg-black/40" onClick={() => setMobileOpen(false)} />
        </div>
      )}
      
      <Modal 
        isOpen={isOpen}
        onClose={hideModal}
        {...modalContent}
      />
    </>
  );
}

export default App;
