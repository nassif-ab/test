import React, { useEffect, useState } from 'react';
import { 
  Chart as ChartJS, 
  ArcElement, 
  Tooltip, 
  Legend,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title
} from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';
import { useAuth } from '../content/AuthProvider';
import axios from 'axios';

// Registrar los componentes necesarios para Chart.js
ChartJS.register(
  ArcElement, 
  Tooltip, 
  Legend,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title
);

// Colores para los gráficos
const backgroundColors = [
  'rgba(255, 99, 132, 0.6)',
  'rgba(54, 162, 235, 0.6)',
  'rgba(255, 206, 86, 0.6)',
  'rgba(75, 192, 192, 0.6)',
  'rgba(153, 102, 255, 0.6)',
  'rgba(255, 159, 64, 0.6)',
  'rgba(199, 199, 199, 0.6)',
  'rgba(83, 102, 255, 0.6)',
  'rgba(40, 159, 64, 0.6)',
  'rgba(210, 199, 199, 0.6)',
];

const borderColors = [
  'rgba(255, 99, 132, 1)',
  'rgba(54, 162, 235, 1)',
  'rgba(255, 206, 86, 1)',
  'rgba(75, 192, 192, 1)',
  'rgba(153, 102, 255, 1)',
  'rgba(255, 159, 64, 1)',
  'rgba(199, 199, 199, 1)',
  'rgba(83, 102, 255, 1)',
  'rgba(40, 159, 64, 1)',
  'rgba(210, 199, 199, 1)',
];

interface UserStats {
  user_id: string;
  username: string;
  total_posts: number;
  total_likes: number;
  total_visits: number;
  favorite_categories: {category: string, count: number}[];
}

interface UserStatsChartProps {
  userId: string;
}

const UserStatsChart: React.FC<UserStatsChartProps> = ({ userId }) => {
  const { token } = useAuth();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`http://localhost:8000/api/users/${userId}/stats`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {}
        });
        setStats(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching user stats:', err);
        setError('حدث خطأ أثناء تحميل إحصائيات المستخدم');
        setLoading(false);
      }
    };

    if (userId) {
      fetchStats();
    }
  }, [userId, token]);

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

  if (!stats) {
    return <div>لا توجد إحصائيات متاحة لهذا المستخدم</div>;
  }

  // Datos para el gráfico de pastel de categorías favoritas
  const categoryPieData = {
    labels: stats.favorite_categories.map(cat => cat.category || 'بدون فئة'),
    datasets: [
      {
        label: 'عدد التفاعلات',
        data: stats.favorite_categories.map(cat => cat.count),
        backgroundColor: backgroundColors,
        borderColor: borderColors,
        borderWidth: 1,
      },
    ],
  };

  // Datos para el gráfico de barras de actividad
  const activityBarData = {
    labels: ['المنشورات', 'الإعجابات', 'الزيارات'],
    datasets: [
      {
        label: 'نشاط المستخدم',
        data: [stats.total_posts, stats.total_likes, stats.total_visits],
        backgroundColor: [
          'rgba(75, 192, 192, 0.6)',
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
        ],
        borderColor: [
          'rgba(75, 192, 192, 1)',
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: `إحصائيات المستخدم: ${stats.username}`,
      },
    },
  };

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Gráfico de pastel para categorías favoritas */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">الفئات المفضلة</h3>
          <div className="h-64">
            <Pie data={categoryPieData} />
          </div>
        </div>

        {/* Gráfico de barras para actividad */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">نشاط المستخدم</h3>
          <div className="h-64">
            <Bar options={options} data={activityBarData} />
          </div>
        </div>
      </div>

      {/* Resumen de estadísticas */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">ملخص الإحصائيات</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-green-50 p-4 rounded-lg">
            <p className="text-sm text-green-600">إجمالي المنشورات</p>
            <p className="text-2xl font-bold">{stats.total_posts}</p>
          </div>
          <div className="bg-pink-50 p-4 rounded-lg">
            <p className="text-sm text-pink-600">إجمالي الإعجابات</p>
            <p className="text-2xl font-bold">{stats.total_likes}</p>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg">
            <p className="text-sm text-blue-600">إجمالي الزيارات</p>
            <p className="text-2xl font-bold">{stats.total_visits}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserStatsChart;
