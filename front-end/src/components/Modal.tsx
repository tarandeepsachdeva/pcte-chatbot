import React, { useState, useEffect } from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  showInput?: boolean;
  initialInputValue?: string;
  onConfirm: (inputValue?: string) => void;
  confirmText?: string;
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  showInput = false,
  initialInputValue = '',
  onConfirm,
  confirmText = 'Confirm',
}) => {
  const [inputValue, setInputValue] = useState(initialInputValue);

  useEffect(() => {
    setInputValue(initialInputValue);
  }, [initialInputValue]);

  if (!isOpen) return null;

  const handleConfirm = () => {
    onConfirm(showInput ? inputValue : undefined);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center">
      <div className="bg-white rounded-lg p-6 shadow-xl w-full max-w-sm">
        <h2 className="text-lg font-bold mb-4">{title}</h2>
        <div className="mb-6 text-sm text-gray-600">{children}</div>
        
        {showInput && (
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md mb-4"
          />
        )}

        <div className="flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
};