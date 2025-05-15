import React, { useEffect, useState } from 'react';
import { useAuth } from '../content/AuthProvider';
import PostStatsChart from '../components/PostStatsChart';
import UserStatsChart from '../components/UserStatsChart';
import axiosClient from '../services/axiosclient';

interface User {
  id: string;
  username: string;
  email: string;
}

const Stats: React.FC = () => {
  const { token } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUserId, setSelectedUserId] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'general' | 'user'>('general');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setLoading(true);
        const response = await axiosClient.get('/users', {
          headers: token ? { Authorization: `Bearer ${token}` } : {}
        });
        setUsers(response.data);
        
        // Seleccionar el primer usuario por defecto si hay usuarios
        if (response.data.length > 0) {
          setSelectedUserId(response.data[0].id);
        }
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching users:', err);
        setError('حدث خطأ أثناء تحميل بيانات المستخدمين');
        setLoading(false);
      }
    };
    
    fetchUsers();
  }, [token]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
        <strong className="font-bold">خطأ!</strong>
        <span className="block sm:inline"> {error}</span>
      </div>
    );
  }

  if (users.length === 0) {
    return <div>لا توجد بيانات متاحة</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">إحصائيات المحتوى واهتمامات المستخدمين</h1>
      
      {/* Pestañas para cambiar entre estadísticas generales y de usuario */}
      <div className="flex mb-6 border-b">
        <button
          className={`px-4 py-2 ${activeTab === 'general' ? 'border-b-2 border-indigo-500 text-indigo-600' : 'text-gray-500'}`}
          onClick={() => setActiveTab('general')}
        >
          إحصائيات عامة
        </button>
        <button
          className={`px-4 py-2 ${activeTab === 'user' ? 'border-b-2 border-indigo-500 text-indigo-600' : 'text-gray-500'}`}
          onClick={() => setActiveTab('user')}
        >
          إحصائيات المستخدمين
        </button>
      </div>
      
      {activeTab === 'general' ? (
        <div>
          <PostStatsChart />
        </div>
      ) : (
        <div>
          <div className="mb-6">
            <label htmlFor="user-select" className="block text-sm font-medium text-gray-700 mb-2">
              اختر المستخدم
            </label>
            <select
              id="user-select"
              className="block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              value={selectedUserId}
              onChange={(e) => setSelectedUserId(e.target.value)}
            >
              {users.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.username}
                </option>
              ))}
            </select>
          </div>
          
          {selectedUserId && <UserStatsChart userId={selectedUserId} />}
        </div>
      )}
    </div>
  );
};

export default Stats;
