import React, { useState } from 'react';
import Login from './Login';
import Register from './Register';
import { useAuth } from '../content/AuthProvider';
import { registerUser } from '../services/api';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose }) => {
  const [showLogin, setShowLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  if (!isOpen) return null;

  const handleLogin = async (username: string, password: string) => {
    setLoading(true);
    try {
      await login(username, password);
      onClose();
    } catch (error: any) {
      console.error('Login error:', error);
      const errorMessage = error.message || 'حدث خطأ أثناء تسجيل الدخول';
      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (username: string, fullName: string, email: string, password: string) => {
    setLoading(true);
    try {
      // إنشاء حساب جديد
      console.log('Attempting to register new user:', username);
      await registerUser(username, fullName, email, password);
      console.log('Registration successful, attempting to login');
      
      // تسجيل الدخول تلقائيًا بعد التسجيل الناجح
      await login(username, password);
      console.log('Auto-login successful after registration');
      
      // إغلاق النافذة بعد نجاح العملية
      onClose();
    } catch (error: any) {
      console.error('Registration error:', error);
      // إظهار رسالة الخطأ للمستخدم
      const errorMessage = error.message || 'حدث خطأ أثناء إنشاء الحساب';
      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="relative w-full max-w-md">
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-gray-500 hover:text-gray-700 z-10"
          aria-label="إغلاق"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        
        
        {loading && (
          <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center z-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#063267]"></div>
          </div>
        )}
        
        
        {showLogin ? (
          <Login 
            onLogin={handleLogin} 
            onSwitchToRegister={() => setShowLogin(false)} 
          />
        ) : (
          <Register 
            onRegister={handleRegister} 
            onSwitchToLogin={() => setShowLogin(true)} 
          />
        )}
      </div>
    </div>
  );
};

export default AuthModal;
