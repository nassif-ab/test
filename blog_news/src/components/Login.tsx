import React, { useState } from 'react';

interface LoginProps {
  onLogin: (username: string, password: string) => void;
  onSwitchToRegister: () => void;
}

const Login: React.FC<LoginProps> = ({ onLogin, onSwitchToRegister }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      setError('Veuillez entrer un nom d\'utilisateur et un mot de passe');
      return;
    }
    onLogin(username, password);
  };

  return (
    <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md mx-auto">
      <h2 className="text-2xl font-bold text-center text-[#063267] mb-6">Se connecter</h2>
      
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
          <button
            type="submit"
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-[#063267] hover:bg-[#052a56] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#063267]"
          >
            Se connecter
          </button>
        </div>
      </form>
      
      <div className="mt-4 text-center">
        <button
          onClick={onSwitchToRegister}
          className="text-sm text-[#063267] hover:underline"
        >
          Vous n'avez pas de compte ? S'inscrire
        </button>
      </div>
    </div>
  );
};

export default Login;
