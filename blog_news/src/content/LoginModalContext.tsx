import React, { createContext, useState, useContext, ReactNode } from 'react';
import AuthModal from '../components/AuthModal';

// Definir el tipo del contexto
interface LoginModalContextType {
  openLoginModal: () => void;
  closeLoginModal: () => void;
  isLoginModalOpen: boolean;
}

// Crear el contexto
const LoginModalContext = createContext<LoginModalContextType | undefined>(undefined);

// Hook personalizado para usar el contexto
export const useLoginModal = () => {
  const context = useContext(LoginModalContext);
  if (context === undefined) {
    throw new Error('useLoginModal debe ser usado dentro de un LoginModalProvider');
  }
  return context;
};

// Props para el proveedor
interface LoginModalProviderProps {
  children: ReactNode;
}

// Componente proveedor
export const LoginModalProvider: React.FC<LoginModalProviderProps> = ({ children }) => {
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);

  const openLoginModal = () => {
    setIsLoginModalOpen(true);
  };

  const closeLoginModal = () => {
    setIsLoginModalOpen(false);
  };

  return (
    <LoginModalContext.Provider value={{ openLoginModal, closeLoginModal, isLoginModalOpen }}>
      {children}
      <AuthModal isOpen={isLoginModalOpen} onClose={closeLoginModal} />
    </LoginModalContext.Provider>
  );
};
