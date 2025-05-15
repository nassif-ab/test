import React from 'react';
import { Link } from 'react-router-dom';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const LoginModal: React.FC<LoginModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-xl max-w-md w-full">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-[#063267]">Connexion requise</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
        <p className="mb-6 text-gray-600">
          Veuillez vous connecter pour aimer cet article et accéder à toutes les fonctionnalités.
        </p>
        <div className="flex flex-col space-y-4">
          <Link
            to="/login"
            className="bg-[#063267] hover:bg-[#0a4a94] text-white py-2 px-4 rounded-md transition-colors duration-300 text-center"
            onClick={onClose}
          >
            Se connecter
          </Link>
          <Link
            to="/register"
            className="border border-[#063267] text-[#063267] hover:bg-gray-100 py-2 px-4 rounded-md transition-colors duration-300 text-center"
            onClick={onClose}
          >
            Créer un compte
          </Link>
        </div>
      </div>
    </div>
  );
};

export default LoginModal;
