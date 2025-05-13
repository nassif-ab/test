import React, { useEffect, useState } from 'react';
import { useAuth } from '../content/AuthProvider';
import { getPostStats, PostStats } from '../services/api';

const Stats: React.FC = () => {
  const { token } = useAuth();
  const [stats, setStats] = useState<PostStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      if (!token) return;
      
      try {
        setLoading(true);
        const data = await getPostStats(token);
        setStats(data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching stats:', err);
        setError('حدث خطأ أثناء تحميل الإحصائيات');
        setLoading(false);
      }
    };
    
    fetchStats();
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
        <strong className="font-bold">خطأ!</strong>
        <span className="block sm:inline"> {error}</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">إحصائيات المحتوى واهتمامات المستخدمين</h1>
      
      {/* Resumen de estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-700">إجمالي المنشورات</h2>
          <p className="text-3xl font-bold text-indigo-600">{stats?.total_posts || 0}</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-700">إجمالي الإعجابات</h2>
          <p className="text-3xl font-bold text-indigo-600">{stats?.total_likes || 0}</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-700">إجمالي الزيارات</h2>
          <p className="text-3xl font-bold text-indigo-600">{stats?.total_visits || 0}</p>
        </div>
      </div>
      
      {/* Categorías populares */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">الفئات الشائعة</h2>
        <div className="relative">
          {/* Gráfico de barras simple */}
          <div className="space-y-2">
            {stats?.popular_categories?.map((category, index) => {
              // Calcular el porcentaje para la anchura de la barra
              const maxCount = Math.max(...stats.popular_categories.map(c => c.count));
              const percentage = (category.count / maxCount) * 100;
              
              return (
                <div key={index} className="flex items-center">
                  <div className="w-32 text-right pr-4">
                    <span className="text-sm font-medium">{category.category || 'بدون فئة'}</span>
                  </div>
                  <div className="flex-1 h-6 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-indigo-600 rounded-full"
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                  <div className="w-12 text-left pl-4">
                    <span className="text-sm">{category.count}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
      
      {/* Posts más populares */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Posts con más likes */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">المنشورات الأكثر إعجابًا</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    العنوان
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    الفئة
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    الإعجابات
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {stats?.most_liked_posts?.map((post) => (
                  <tr key={post.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {post.title}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {post.categorie || 'بدون فئة'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {post.likes || 0}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        
        {/* Posts más visitados */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">المنشورات الأكثر زيارة</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    العنوان
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    الفئة
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    الزيارات
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {stats?.most_visited_posts?.map((post) => (
                  <tr key={post.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {post.title}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {post.categorie || 'بدون فئة'}
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
      </div>
      
      {/* Análisis de intereses de usuarios */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">تحليل اهتمامات المستخدمين</h2>
        <div className="prose max-w-none">
          <p className="text-gray-700">
            بناءً على تحليل تفاعلات المستخدمين (الإعجابات والزيارات)، يمكن استنتاج أن اهتمامات المستخدمين تتركز في الفئات التالية:
          </p>
          
          <ul className="mt-4 space-y-2">
            {stats?.popular_categories?.slice(0, 3).map((category, index) => (
              <li key={index} className="flex items-center">
                <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-indigo-100 text-indigo-800 font-medium text-sm mr-2">
                  {index + 1}
                </span>
                <span>
                  <strong>{category.category || 'بدون فئة'}</strong> - يظهر اهتمام كبير من المستخدمين بهذه الفئة مع {category.count} منشور.
                </span>
              </li>
            ))}
          </ul>
          
          <div className="mt-6 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
            <h3 className="text-lg font-medium text-yellow-800">توصيات لتحسين المحتوى:</h3>
            <ul className="mt-2 space-y-1 list-disc list-inside text-yellow-700">
              <li>زيادة المحتوى في الفئات الأكثر شعبية لتلبية اهتمامات المستخدمين.</li>
              <li>تحسين جودة المحتوى في الفئات الأقل زيارة لزيادة الاهتمام بها.</li>
              <li>النظر في إنشاء فئات جديدة بناءً على اتجاهات اهتمامات المستخدمين.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Stats;
