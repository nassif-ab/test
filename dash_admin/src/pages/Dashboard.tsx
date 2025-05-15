import React, { useEffect, useState } from 'react';
import { useAuth } from '../content/AuthProvider';
import { getPostStats, PostStats, getPosts, Post, getUsers, User } from '../services/api';

const Dashboard: React.FC = () => {
  const { token } = useAuth();
  const [stats, setStats] = useState<PostStats | null>(null);
  const [recentPosts, setRecentPosts] = useState<Post[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      if (!token) return;
      
      try {
        setLoading(true);
        
        // Obtener estadísticas generales
        const statsData = await getPostStats(token);
        setStats(statsData);
        
        // Obtener posts recientes
        const postsData = await getPosts(token);
        setRecentPosts(postsData.slice(0, 5)); // Solo los 5 más recientes
        
        // Obtener usuarios
        const usersData = await getUsers(token);
        setUsers(usersData.slice(0, 5)); // Solo los 5 más recientes
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Une erreur s\'est produite lors du chargement des données');
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, [token]);

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
      <h1 className="text-3xl font-bold text-gray-800">Tableau de Bord</h1>
      
      {/* Tarjetas de estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-700">Total des Publications</h2>
          <p className="text-3xl font-bold text-indigo-600">{stats?.total_posts || 0}</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-700">Total des Likes</h2>
          <p className="text-3xl font-bold text-indigo-600">{stats?.total_likes || 0}</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-700">Total des Visites</h2>
          <p className="text-3xl font-bold text-indigo-600">{stats?.total_visits || 0}</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-700">Utilisateurs</h2>
          <p className="text-3xl font-bold text-indigo-600">{users.length}</p>
        </div>
      </div>
      
      {/* Categorías populares */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Catégories Populaires</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {stats?.popular_categories?.map((category, index) => (
            <div key={index} className="bg-indigo-50 rounded-lg p-4">
              <h3 className="font-medium text-indigo-700">{category.category || 'Sans catégorie'}</h3>
              <p className="text-gray-600">{category.count} publications</p>
            </div>
          ))}
        </div>
      </div>
      
      {/* Posts recientes */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Publications Récentes</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Titre
                </th>
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Catégorie
                </th>
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Likes
                </th>
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Visites
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {recentPosts.map((post) => (
                <tr key={post.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {post.title}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {post.categorie || 'Sans catégorie'}
                    </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {post.likes || 0}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {post.visits || 0}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
      {/* Usuarios recientes */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Utilisateurs</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date d'inscription
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {user.username}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {user.email || '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
