import React, { useState } from 'react';
import { useAuth } from '../content/AuthProvider';
import { likePost } from '../services/api';
import { Link } from 'react-router-dom';
import { useLoginModal } from '../content/LoginModalContext';

interface PostCardProps {
  titre: string;
  image: string;
  contenu: string;
  isliked: boolean;
  likes: number;
  visits: number;
  id?: string; // Añadir ID del post para poder dar like
  categorie?: string; // Añadir categoría del post
}

const PostCard: React.FC<PostCardProps> = ({ id, titre, image, contenu, isliked=false, likes=0, visits=0, categorie="" }) => {
  const { token, isAuthenticated } = useAuth();
  const { openLoginModal } = useLoginModal();
  const [liked, setLiked] = useState(isliked);
  const [likeCount, setLikeCount] = useState(likes);
  const [isLiking, setIsLiking] = useState(false);
  const [visitCount, setVisitCount] = useState(visits);

  const handleLike = async () => {
    console.log('handleLike llamado');
    console.log('isAuthenticated:', isAuthenticated);
    console.log('id:', id);
    console.log('isLiking:', isLiking);
    console.log('token:', token ? 'Existe' : 'No existe');
    
    if (!isAuthenticated) {
      console.log('No autenticado, mostrando modal de login');
      openLoginModal();
      return;
    }
    
    if (!id) {
      console.log('No hay ID de post, saliendo');
      return;
    }
    
    if (isLiking) {
      console.log('Ya está en proceso de like, saliendo');
      return;
    }
    
    try {
      console.log('Iniciando petición de like para post ID:', id);
      setIsLiking(true);
      await likePost(id, token!);
      console.log('Like completado con éxito');
      
      // Toggle like state and update count
      if (liked) {
        setLikeCount(prev => Math.max(0, prev - 1));
        console.log('Quitando like, nuevo contador:', likeCount - 1);
      } else {
        setLikeCount(prev => prev + 1);
        console.log('Añadiendo like, nuevo contador:', likeCount + 1);
      }
      setLiked(!liked);
      console.log('Estado de like actualizado a:', !liked);
    } catch (error) {
      console.error('Error al dar like:', error);
    } finally {
      setIsLiking(false);
      console.log('Estado isLiking restablecido a false');
    }
  };

  return (
    <div className="bg-white rounded-lg overflow-hidden shadow-lg transition-transform duration-300 hover:shadow-xl hover:-translate-y-1">
      <img 
        src={image} 
        alt={titre} 
        className="w-full h-48 object-cover"
        onError={(e) => {
          const target = e.target as HTMLImageElement;
          target.src = 'https://placehold.co/400x200/ff0808/ffffff';
        }}
      />
      <div className="p-6">
        {categorie && (
          <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full mb-2">
            {categorie}
          </span>
        )}
        <h3 className="text-xl font-bold mb-2 text-[#063267]">{titre}</h3>
        <p className="text-gray-700 text-base line-clamp-3" dangerouslySetInnerHTML={{ __html: contenu.substring(0, 150) + '...' }} />
        <div className="mt-4 flex justify-between items-center">
          <Link to={`/post/${id}`} className="bg-[#063267] hover:bg-[#0a4a94] text-white py-2 px-4 rounded-md transition-colors duration-300 inline-block">
            Lire la suite
          </Link>
          
          {/* Estadísticas del post */}
          <div className="flex items-center space-x-2">
            {/* Botón de like */}
            <button 
              onClick={handleLike}
              disabled={isLiking}
              className={`flex items-center gap-1 px-3 py-1 rounded-full transition-colors ${liked ? 'text-red-500' : 'text-gray-500'} hover:bg-gray-100`}
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
              <span>{likeCount}</span>
            </button>
            
            {/* Contador de visitas */}
            <div className="flex items-center gap-1 px-3 py-1 text-gray-500" title="Visitas">
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
              <span>{visitCount}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PostCard;
