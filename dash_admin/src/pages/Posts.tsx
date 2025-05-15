import React, { useEffect, useState } from 'react';
import { useAuth } from '../content/AuthProvider';
import { getPosts, Post, deletePost, createPost, updatePost } from '../services/api';

const Posts: React.FC = () => {
  const { token } = useAuth();
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingPost, setEditingPost] = useState<Post | null>(null);
  
  // Estado para el formulario
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    categorie: '',
    image: ''
  });

  useEffect(() => {
    fetchPosts();
  }, [token]);

  const fetchPosts = async () => {
    if (!token) return;
    
    try {
      setLoading(true);
      const data = await getPosts(token);
      setPosts(data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching posts:', err);
      setError('Une erreur s\'est produite lors du chargement des publications');
      setLoading(false);
    }
  };

  const handleDeletePost = async (postId: string) => {
    if (!token) return;
    
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cette publication?')) {
      try {
        await deletePost(postId, token);
        setPosts(posts.filter(post => post.id !== postId));
      } catch (err) {
        console.error('Error deleting post:', err);
        setError('Une erreur s\'est produite lors de la suppression de la publication');
      }
    }
  };

  const handleCreatePost = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    
    try {
      setLoading(true);
      if (editingPost) {
        // Actualizar post existente
        await updatePost(editingPost.id, formData, token);
      } else {
        // Crear nuevo post
        await createPost(formData, token);
      }
      
      // Limpiar formulario y recargar posts
      setFormData({ title: '', content: '', categorie: '', image: '' });
      setShowForm(false);
      setEditingPost(null);
      await fetchPosts();
    } catch (err) {
      console.error('Error saving post:', err);
      setError('Une erreur s\'est produite lors de l\'enregistrement de la publication');
      setLoading(false);
    }
  };

  const handleEditPost = (post: Post) => {
    setEditingPost(post);
    setFormData({
      title: post.title,
      content: post.content,
      categorie: post.categorie || '',
      image: post.image || ''
    });
    setShowForm(true);
    setTimeout(() => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 100); // تأخير بسيط للسماح بإظهار النموذج أولًا
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  if (loading && posts.length === 0) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-800">Gestion des publications</h1>
        <button 
          onClick={() => {
            setEditingPost(null);
            setFormData({ title: '', content: '', categorie: '', image: '' });
            setShowForm(!showForm);
          }}
          className="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded"
        >
          {showForm ? 'Annuler' : 'Ajouter une nouvelle publication'}
        </button>
      </div>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Erreur!</strong>
          <span className="block sm:inline"> {error}</span>
        </div>
      )}
      
      {/* Formulario para crear/editar posts */}
      {showForm && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            {editingPost ? 'Modifier la publication' : 'Ajouter une nouvelle publication'}
          </h2>
          
          <form onSubmit={handleCreatePost} className="space-y-4">
            <div>
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="title">
                Titre
              </label>
              <input
                id="title"
                name="title"
                type="text"
                required
                value={formData.title}
                onChange={handleInputChange}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              />
            </div>
            
            <div>
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="categorie">
                Catégorie
              </label>
              <input
                id="categorie"
                name="categorie"
                type="text"
                value={formData.categorie}
                onChange={handleInputChange}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              />
            </div>
            
            <div>
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="image">
                URL de l'image
              </label>
              <input
                id="image"
                name="image"
                type="text"
                value={formData.image}
                onChange={handleInputChange}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              />
            </div>
            
            <div>
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="content">
                Contenu
              </label>
              <textarea
                id="content"
                name="content"
                required
                value={formData.content}
                onChange={handleInputChange}
                rows={6}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              />
            </div>
            
            <div className="flex justify-end">
              <button
                type="submit"
                className="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded"
              >
                {editingPost ? 'Mettre à jour la publication' : 'Créer la publication'}
              </button>
            </div>
          </form>
        </div>
      )}
      
      {/* Tabla de posts */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
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
                J'aime
              </th>
              <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Visites
              </th>
              <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {posts.map((post) => (
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
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 space-x-2 flex space-x-reverse gap-2">
                  <button 
                    onClick={() =>{ handleEditPost(post)
                      }}
                    className="text-indigo-600 hover:text-indigo-900"
                  >
                    Modifier
                  </button>
                  <button 
                    onClick={() => handleDeletePost(post.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Supprimer
                  </button>
                </td>
              </tr>
            ))}
            
            {posts.length === 0 && !loading && (
              <tr>
                <td colSpan={5} className="px-6 py-4 text-center text-sm text-gray-500">
                  Aucune publication disponible
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Posts;
