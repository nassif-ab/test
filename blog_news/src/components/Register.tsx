import React, { useState } from 'react';

interface RegisterProps {
  onRegister: (username: string, email: string, password: string) => void;
  onSwitchToLogin: () => void;
}

const Register: React.FC<RegisterProps> = ({ onRegister, onSwitchToLogin }) => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validación básica
    if (!username.trim() || !email.trim() || !password.trim()) {
      setError('الرجاء إدخال جميع الحقول المطلوبة');
      return;
    }
    
    if (password !== confirmPassword) {
      setError('كلمات المرور غير متطابقة');
      return;
    }
    
    // Validación simple de email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError('الرجاء إدخال بريد إلكتروني صحيح');
      return;
    }
    
    onRegister(username, email, password);
  };

  return (
    <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md mx-auto">
      <h2 className="text-2xl font-bold text-center text-[#063267] mb-6">إنشاء حساب جديد</h2>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4 text-right">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="username" className="block text-sm font-medium text-gray-700 text-right">
            اسم المستخدم
          </label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-[#063267] focus:border-[#063267]"
            dir="rtl"
          />
        </div>
        
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 text-right">
            البريد الإلكتروني
          </label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-[#063267] focus:border-[#063267]"
            dir="rtl"
          />
        </div>
        
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700 text-right">
            كلمة المرور
          </label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-[#063267] focus:border-[#063267]"
            dir="rtl"
          />
        </div>
        
        <div>
          <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 text-right">
            تأكيد كلمة المرور
          </label>
          <input
            type="password"
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-[#063267] focus:border-[#063267]"
            dir="rtl"
          />
        </div>
        
        <div>
          <button
            type="submit"
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-[#063267] hover:bg-[#052a56] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#063267]"
          >
            إنشاء حساب
          </button>
        </div>
      </form>
      
      <div className="mt-4 text-center">
        <button
          onClick={onSwitchToLogin}
          className="text-sm text-[#063267] hover:underline"
        >
          لديك حساب بالفعل؟ تسجيل الدخول
        </button>
      </div>
    </div>
  );
};

export default Register;
