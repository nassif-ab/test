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
  Title,
  TimeScale,
  BarElement
} from 'chart.js';
import { Pie, Line, Bar } from 'react-chartjs-2';
import { useAuth } from '../content/AuthProvider';
import 'chartjs-adapter-date-fns';
import axiosClient from '../services/axiosclient';

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
  TimeScale,
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

interface PostStats {
  total_posts: number;
  total_likes: number;
  total_visits: number;
  popular_categories: {category: string, count: number}[];
  most_liked_posts: any[];
  most_visited_posts: any[];
  visits_by_time: {date: string, count: number}[];
}

const PostStatsChart: React.FC = () => {
  const { token } = useAuth();
  const [stats, setStats] = useState<PostStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const response = await axiosClient.get('/posts/stats', {
          headers: token ? { Authorization: `Bearer ${token}` } : {}
        });
        setStats(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching stats:', err);
        setError('Une erreur s\'est produite lors du chargement des statistiques');
        setLoading(false);
      }
    };

    fetchStats();
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
        <strong className="font-bold">Erreur!</strong>
        <span className="block sm:inline"> {error}</span>
      </div>
    );
  }

  if (!stats) {
    return <div>Aucune statistique disponible</div>;
  }

  // Datos para el gráfico de pastel de categorías
  const categoryPieData = {
    labels: stats.popular_categories.map(cat => cat.category || 'Sans catégorie'),
    datasets: [
      {
        label: 'Nombre de publications',
        data: stats.popular_categories.map(cat => cat.count),
        backgroundColor: backgroundColors,
        borderColor: borderColors,
        borderWidth: 1,
      },
    ],
  };

  // Datos para el gráfico de línea de posts más populares
  const popularPostsLineData = {
    labels: stats.most_liked_posts.map(post => post.title.substring(0, 15) + '...'),
    datasets: [
      {
        label: 'J\'aime',
        data: stats.most_liked_posts.map(post => post.likes),
        borderColor: 'rgba(255, 99, 132, 1)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        tension: 0.4,
      },
      {
        label: 'Visits',
        data: stats.most_liked_posts.map(post => post.visits),
        borderColor: 'rgba(54, 162, 235, 1)',
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        tension: 0.4,
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
        text: 'Statistiques des publications',
      },
    },
  };

  // Preparar datos para el gráfico de visitas por tiempo
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
  };

  const visitsTimeData = {
    labels: stats?.visits_by_time?.map(item => formatDate(item.date)) || [],
    datasets: [
      {
        label: 'Visits',
        data: stats?.visits_by_time?.map(item => item.count) || [],
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 2,
        tension: 0.4,
        fill: true,
      },
    ],
  };

  const timeChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Visites par période (7 derniers jours)',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Nombre de visites'
        }
      },
      x: {
        title: {
          display: true,
          text: 'Date'
        }
      }
    },
  };

  return (
    <div className="space-y-8">
      {/* Gráfico de visitas por tiempo */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Visites totales par période</h3>
        <div className="h-64">
          <Line options={timeChartOptions} data={visitsTimeData} />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Gráfico de pastel para categorías */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Distribution des catégories</h3>
          <div className="h-64">
            <Pie data={categoryPieData} />
          </div>
        </div>

        {/* Gráfico de línea para likes y visitas */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">J'aime et visites des publications les plus populaires</h3>
          <div className="h-64">
            <Line options={options} data={popularPostsLineData} />
          </div>
        </div>
      </div>

      {/* Resumen de estadísticas */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Résumé des statistiques</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-indigo-50 p-4 rounded-lg">
            <p className="text-sm text-indigo-600">Total des publications</p>
            <p className="text-2xl font-bold">{stats.total_posts}</p>
          </div>
          <div className="bg-pink-50 p-4 rounded-lg">
            <p className="text-sm text-pink-600">Total des j'aime</p>
            <p className="text-2xl font-bold">{stats.total_likes}</p>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg">
            <p className="text-sm text-blue-600">Total des visites</p>
            <p className="text-2xl font-bold">{stats.total_visits}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PostStatsChart;
