import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../content/AuthProvider';
import { getPostById, recordVisit, likePost, getSimilarPosts } from '../services/api';
import { PostUI } from '../services/api';

const PostDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { token, isAuthenticated } = useAuth();
  const [post, setPost] = useState<PostUI | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [liked, setLiked] = useState(false);
  const [likeCount, setLikeCount] = useState(0);
  const [isLiking, setIsLiking] = useState(false);
  const [visitCount, setVisitCount] = useState(0);
const [similarPosts, setSimilarPosts] = useState<PostUI[]>([]);

  // Cargar los datos del post
  useEffect(() => {
    const fetchPost = async () => {
      if (!id) return;
      
      try {
        setLoading(true);
        const fetchedPost = await getPostById(id, token || undefined);
        
        if (fetchedPost) {
          setPost({
            id: fetchedPost.id,
            titre: fetchedPost.title,
            image: fetchedPost.image || "/post.jpg",
            contenu: fetchedPost.content,
            isliked: fetchedPost.isliked || false,
            likes: fetchedPost.likes || 0,
            visits: fetchedPost.visits || 0,
            categorie: fetchedPost.categorie
          });
          setLiked(fetchedPost.isliked || false);
          setLikeCount(fetchedPost.likes || 0);
          setVisitCount(fetchedPost.visits || 0);
          const similar = await getSimilarPosts(id);
          setSimilarPosts(similar);
        } else {
          setError("Post no encontrado");
        }
      } catch (err) {
        console.error("Error al cargar el post:", err);
        setError("Error al cargar el post");
      } finally {
        setLoading(false);
      }
    };

    fetchPost();
  }, [id, token]);

  

  // Registrar una visita cuando se carga la página
  useEffect(() => {
    if (id && !loading && post) {
      // Registrar la visita (funciona para usuarios autenticados y anónimos)
      recordVisit(id, token || undefined)
        .then(() => {
          // Incrementar el contador de visitas localmente
          setVisitCount(prev => prev + 1);
        })
        .catch(error => {
          console.error('Error al registrar visita:', error);
        });
    }
  }, [id, loading, post, token]);

  const handleLike = async () => {
    if (!isAuthenticated || !id || isLiking) {
      return;
    }

    try {
      setIsLiking(true);
      await likePost(id, token!);
      
      // Toggle like state and update count
      if (liked) {
        setLikeCount(prev => Math.max(0, prev - 1));
      } else {
        setLikeCount(prev => prev + 1);
      }
      setLiked(!liked);
    } catch (error) {
      console.error('Error al dar like:', error);
    } finally {
      setIsLiking(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8 flex justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#063267]"></div>
      </div>
    );
  }

  if (error || !post) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p>{error || "Post no encontrado"}</p>
          <button 
            onClick={() => navigate('/')}
            className="mt-2 bg-[#063267] hover:bg-[#0a4a94] text-white py-2 px-4 rounded-md transition-colors duration-300"
          >
            Volver a la página principal
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto bg-white rounded-lg overflow-hidden shadow-xl">
        {/* Imagen del post */}
        <img 
          src={post.image} 
          alt={post.titre} 
          className="w-full h-64 object-cover"
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            target.src = 'https://placehold.co/800x400/ff0808/ffffff';
          }}
        />
        
        {/* Contenido del post */}
        <div className="p-8">
          {post.categorie && (
            <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full mb-2">
              {post.categorie}
            </span>
          )}
          <h1 className="text-3xl font-bold mb-4 text-[#063267]">{post.titre}</h1>
          
          {/* Estadísticas */}
          <div className="flex items-center space-x-4 mb-6 text-gray-500">
            {/* Contador de visitas */}
            <div className="flex items-center gap-1">
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                className="h-5 w-5" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              <span>{visitCount} visitas</span>
            </div>
            
            {/* Botón de like */}
            <button 
              onClick={handleLike}
              disabled={!isAuthenticated || isLiking}
              className={`flex items-center gap-1 transition-colors ${liked ? 'text-red-500' : 'text-gray-500'} ${isAuthenticated ? 'hover:text-red-500' : ''}`}
              title={isAuthenticated ? 'Me gusta' : 'Inicia sesión para dar like'}
            >
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                className="h-5 w-5" 
                fill={liked ? "currentColor" : "none"} 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
              <span>{likeCount} likes</span>
            </button>
          </div>
          
          {/* Contenido completo */}
          <div className="prose max-w-none">
            <p className="text-gray-700 text-lg leading-relaxed whitespace-pre-line">
              {post.contenu}
            </p>
          </div>
          
          {/* Botón para volver */}
          <div className="mt-8">
            <button 
              onClick={() => navigate('/')}
              className="bg-[#063267] hover:bg-[#0a4a94] text-white py-2 px-4 rounded-md transition-colors duration-300"
            >
              Volver a la página principal
            </button>
          </div>
        </div>
      </div>


      <div className="mt-8">
  <h2 className="text-2xl font-bold mb-4 text-[#063267]">Posts similares</h2>
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    {similarPosts.map((post) => (
      <div key={post.id} className="bg-white rounded-lg overflow-hidden shadow-md">
        <img 
          src={post.image} 
          alt={post.titre} 
          className="w-full h-32 object-cover"
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            target.src = 'https://placehold.co/400x200/ff0808/ffffff';
          }}
        />
        <div className="p-4">
          {post.categorie && (
            <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full mb-2">
              {post.categorie}
            </span>
          )}
          <h3 className="font-bold text-lg mb-2 text-[#063267]">{post.titre}</h3>
          <p className="text-gray-700 text-sm line-clamp-2">{post.contenu}</p>
          <Link 
            to={`/post/${post.id}`} 
            className="mt-2 inline-block text-sm text-[#063267] hover:underline"
          >
            Leer más
          </Link>
        </div>
      </div>
    ))}
  </div>
</div>
    </div>
  );
};

export default PostDetail;
