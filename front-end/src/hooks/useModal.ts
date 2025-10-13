import { useState } from 'react';

export const useModal = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [modalContent, setModalContent] = useState<any>({});

  const showModal = (content: any) => {
    setModalContent(content);
    setIsOpen(true);
  };

  const hideModal = () => {
    setIsOpen(false);
    setModalContent({});
  };

  return {
    isOpen,
    showModal,
    hideModal,
    modalContent,
  };
};