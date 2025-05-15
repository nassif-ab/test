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
      setError('Veuillez entrer tous les champs requis');
      return;
    }
    
    if (password !== confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      return;
    }
    
    // Validación simple de email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError('Veuillez entrer un email valide');
      return;
    }
    
    onRegister(username, email, password);
  };

  return (
    <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md mx-auto">
      <h2 className="text-2xl font-bold text-center text-[#063267] mb-6">Créer un compte</h2>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4 text-right">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="username" className="block text-sm font-medium text-gray-700 text-right">
            Nom d'utilisateur
          </label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-[#063267] focus:border-[#063267]"
            
          />
        </div>
        
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 text-right">
            Email
          </label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-[#063267] focus:border-[#063267]"
            
          />
        </div>
        
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700 text-right">
            Mot de passe
          </label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-[#063267] focus:border-[#063267]"
            
          />
        </div>
        
        <div>
          <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 text-right">
            Confirmer le mot de passe
          </label>
          <input
            type="password"
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-[#063267] focus:border-[#063267]"
            
          />
        </div>
        
        <div>
          <button
            type="submit"
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-[#063267] hover:bg-[#052a56] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#063267]"
          >
            Créer un compte
          </button>
        </div>
      </form>
      
      <div className="mt-4 text-center">
        <button
          onClick={onSwitchToLogin}
          className="text-sm text-[#063267] hover:underline"
        >
          Vous avez déjà un compte ? Se connecter
        </button>
      </div>
    </div>
  );
};

export default Register;
