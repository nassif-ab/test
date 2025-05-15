import React, { useEffect, useState } from 'react';
import { useAuth } from '../content/AuthProvider';
import { getUsers, User, getUserStats, UserStats } from '../services/api';

const Users: React.FC = () => {
  const { token } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUser, setSelectedUser] = useState<string | null>(null);
  const [userStats, setUserStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [statsLoading, setStatsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUsers = async () => {
      if (!token) return;
      
      try {
        setLoading(true);
        const data = await getUsers(token);
        setUsers(data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching users:', err);
        setError('Une erreur s\'est produite lors du chargement des données utilisateurs');
        setLoading(false);
      }
    };
    
    fetchUsers();
  }, [token]);

  const handleUserSelect = async (userId: string) => {
    if (!token) return;
    
    try {
      setSelectedUser(userId);
      setStatsLoading(true);
      const stats = await getUserStats(userId, token);
      setUserStats(stats);
      setStatsLoading(false);
    } catch (err) {
      console.error('Error fetching user stats:', err);
      setError('Une erreur s\'est produite lors du chargement des statistiques utilisateur');
      setStatsLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <strong className="font-bold">Erreur!</strong>
        <span className="block sm:inline"> {error}</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">Gestion des Utilisateurs</h1>
      
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Lista de usuarios */}
        <div className="lg:w-1/2 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Utilisateurs</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Nom d'utilisateur
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map((user) => (
                  <tr key={user.id} className={selectedUser === user.id ? 'bg-indigo-50' : ''}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {user.username}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {user.email || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <button 
                        onClick={() => handleUserSelect(user.id)}
                        className="text-indigo-600 hover:text-indigo-900"
                      >
                        Voir détails
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        
        {/* Detalles del usuario seleccionado */}
        <div className="lg:w-1/2 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Détails de l'utilisateur</h2>
          
          {!selectedUser ? (
            <div className="text-center py-10 text-gray-500">
              Sélectionnez un utilisateur pour voir les détails
            </div>
          ) : statsLoading ? (
            <div className="flex justify-center items-center py-10">
              <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-indigo-500"></div>
            </div>
          ) : userStats ? (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium">{userStats.username}</h3>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-indigo-50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-indigo-700">Publications</h4>
                  <p className="text-2xl font-bold text-indigo-900">{userStats.total_posts}</p>
                </div>
                <div className="bg-indigo-50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-indigo-700">J'aime</h4>
                  <p className="text-2xl font-bold text-indigo-900">{userStats.total_likes}</p>
                </div>
                <div className="bg-indigo-50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-indigo-700">Visites</h4>
                  <p className="text-2xl font-bold text-indigo-900">{userStats.total_visits}</p>
                </div>
              </div>
              
              <div>
                <h4 className="text-lg font-medium mb-2">Catégories favorites</h4>
                {userStats.favorite_categories.length > 0 ? (
                  <div className="grid grid-cols-2 gap-2">
                    {userStats.favorite_categories.map((category, index) => (
                      <div key={index} className="bg-gray-100 rounded p-2 flex justify-between">
                        <span className="font-medium">{category.category || 'Sans catégorie'}</span>
                        <span className="text-gray-600">{category.count}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">Aucune catégorie favorite</p>
                )}
              </div>
            </div>
          ) : (
            <div className="text-center py-10 text-gray-500">
              Aucune donnée disponible pour cet utilisateur
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Users;
