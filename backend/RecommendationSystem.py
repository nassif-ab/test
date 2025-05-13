from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import datetime
import logging

# Import models
from models import User, Post, Like, Visit
import models
from database import SessionLocal

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RecommendationSystem:
    def __init__(self):
        self.db = SessionLocal()
        # Cache para resultados de recomendaciones
        self.user_based_recommendations_cache = {}
        self.content_based_recommendations_cache = {}
        self.similar_posts_cache = {}
        # Cuándo se actualizó el caché por última vez
        self.last_cache_update = datetime.datetime.now()
        # Tiempo de expiración del caché (12 horas)
        self.cache_expiry = datetime.timedelta(hours=12)
        
    def _is_cache_valid(self):
        """Verifica si el caché es válido o ha expirado"""
        return (datetime.datetime.now() - self.last_cache_update) < self.cache_expiry
        
    def _build_user_item_matrix(self) -> Tuple[np.ndarray, List[int], List[int]]:
        """
        Construye una matriz usuario-item basada en likes y visitas
        
        Returns:
            Tuple[np.ndarray, List[int], List[int]]: La matriz, lista de IDs de usuarios, lista de IDs de posts
        """
        try:
            # Obtener todos los usuarios y posts
            users = self.db.query(User).all()
            posts = self.db.query(Post).all()
            
            user_ids = [user.id for user in users]
            post_ids = [post.id for post in posts]
            
            # Crear matriz de interacciones
            matrix = np.zeros((len(user_ids), len(post_ids)))
            
            # Llenar la matriz con likes (peso 2) y visitas (peso 1)
            for i, user_id in enumerate(user_ids):
                # Obtener likes del usuario
                likes = self.db.query(Like).filter(Like.user_id == user_id).all()
                for like in likes:
                    if like.post_id in post_ids:
                        j = post_ids.index(like.post_id)
                        matrix[i, j] += 2  # Peso mayor para likes
                
                # Obtener visitas del usuario
                visits = self.db.query(Visit).filter(Visit.user_id == user_id).all()
                for visit in visits:
                    if visit.post_id in post_ids:
                        j = post_ids.index(visit.post_id)
                        matrix[i, j] += 1  # Peso menor para visitas
            
            return matrix, user_ids, post_ids
        except Exception as e:
            logger.error(f"Error al construir la matriz usuario-item: {e}")
            return np.array([]), [], []
    
    def _apply_svd(self, matrix: np.ndarray, n_components: int = 10) -> np.ndarray:
        """
        Aplica SVD a la matriz usuario-item
        
        Args:
            matrix (np.ndarray): Matriz usuario-item
            n_components (int, optional): Número de componentes. Default es 10.
            
        Returns:
            np.ndarray: Matriz reconstruida después de SVD
        """
        if matrix.shape[0] < 2 or matrix.shape[1] < 2:
            logger.warning("Matriz demasiado pequeña para SVD")
            return matrix
            
        # Ajustar el número de componentes si es necesario
        n_components = min(n_components, min(matrix.shape[0]-1, matrix.shape[1]-1))
        
        try:
            # Aplicar SVD
            svd = TruncatedSVD(n_components=n_components)
            matrix_reduced = svd.fit_transform(matrix)
            reconstructed_matrix = matrix_reduced @ svd.components_
            return reconstructed_matrix
        except Exception as e:
            logger.error(f"Error al aplicar SVD: {e}")
            return matrix
    
    def get_recommendations_for_user(self, user_id: int, n_recommendations: int = 5) -> List[Dict]:
        """
        Obtiene recomendaciones para un usuario basadas en sus interacciones
        
        Args:
            user_id (int): ID del usuario
            n_recommendations (int, optional): Número de recomendaciones. Default es 5.
            
        Returns:
            List[Dict]: Lista de posts recomendados
        """
        # Verificar si hay recomendaciones en caché
        if self._is_cache_valid() and user_id in self.user_based_recommendations_cache:
            return self.user_based_recommendations_cache[user_id][:n_recommendations]
        
        try:
            # Obtener las categorías preferidas del usuario basadas en sus interacciones
            user_likes = self.db.query(Like).filter(Like.user_id == user_id).all()
            user_visits = self.db.query(Visit).filter(Visit.user_id == user_id).all()
            
            interacted_post_ids = set([like.post_id for like in user_likes] + 
                                    [visit.post_id for visit in user_visits])
            
            # Si el usuario no ha interactuado con ningún post, devolver los posts populares
            if not interacted_post_ids:
                logger.info(f"Usuario {user_id} no tiene interacciones, devolviendo posts populares")
                return self._get_popular_posts(n_recommendations)
            
            # Obtener las categorías de los posts con los que ha interactuado el usuario
            interacted_posts = self.db.query(Post).filter(Post.id.in_(interacted_post_ids)).all()
            
            # Contar las interacciones por categoría
            category_weights = defaultdict(int)
            for post in interacted_posts:
                # Dar más peso a los likes (x3) que a las visitas (x1)
                like_weight = 3 if post.id in [like.post_id for like in user_likes] else 0
                visit_weight = 1 if post.id in [visit.post_id for visit in user_visits] else 0
                category_weights[post.categorie] += (like_weight + visit_weight)
            
            # Ordenar categorías por peso
            sorted_categories = sorted(category_weights.items(), key=lambda x: x[1], reverse=True)
            logger.info(f"Categorías preferidas del usuario {user_id}: {sorted_categories}")
            
            # Si hay categorías preferidas, priorizar posts de esas categorías
            if sorted_categories:
                # Obtener posts no interactuados de las categorías preferidas
                preferred_categories = [cat for cat, _ in sorted_categories]
                
                # Construir matriz usuario-item solo si es necesario para SVD
                matrix, user_ids, post_ids = self._build_user_item_matrix()
                
                if user_id in user_ids:
                    # Aplicar SVD para obtener recomendaciones personalizadas
                    reconstructed_matrix = self._apply_svd(matrix)
                    user_idx = user_ids.index(user_id)
                    user_scores = reconstructed_matrix[user_idx]
                    
                    # Obtener todos los posts no interactuados
                    all_posts = self.db.query(Post).filter(~Post.id.in_(interacted_post_ids)).all()
                    
                    # Calcular puntuación combinada (SVD + categoría)
                    post_scores = []
                    for post in all_posts:
                        if post.id in post_ids:
                            post_idx = post_ids.index(post.id)
                            svd_score = user_scores[post_idx]
                            
                            # Bonus por categoría preferida
                            category_bonus = 0
                            for i, (cat, _) in enumerate(sorted_categories):
                                if post.categorie == cat:
                                    # Dar más peso a las categorías más preferidas
                                    category_bonus = (len(sorted_categories) - i) / len(sorted_categories) * 5
                                    break
                            
                            # Puntuación combinada
                            combined_score = svd_score + category_bonus
                            post_scores.append((post, combined_score))
                    
                    # Ordenar por puntuación combinada
                    post_scores.sort(key=lambda x: x[1], reverse=True)
                    recommended_posts = [ps[0] for ps in post_scores[:n_recommendations]]
                else:
                    # Si el usuario no está en la matriz, recomendar por categoría
                    recommended_posts = []
                    remaining = n_recommendations
                    
                    # Distribuir recomendaciones entre categorías preferidas
                    for category, _ in sorted_categories:
                        if remaining <= 0:
                            break
                        
                        # Obtener posts no interactuados de esta categoría
                        category_posts = self.db.query(Post).filter(
                            Post.categorie == category,
                            ~Post.id.in_(interacted_post_ids)
                        ).order_by(Post.created_at.desc()).limit(remaining).all()
                        
                        recommended_posts.extend(category_posts)
                        remaining -= len(category_posts)
                    
                    # Si aún faltan recomendaciones, añadir posts populares
                    if remaining > 0:
                        popular_posts = self.db.query(Post).filter(
                            ~Post.id.in_(interacted_post_ids),
                            ~Post.id.in_([p.id for p in recommended_posts])
                        ).order_by(Post.created_at.desc()).limit(remaining).all()
                        
                        recommended_posts.extend(popular_posts)
            else:
                # Fallback a posts populares si no hay categorías preferidas
                return self._get_popular_posts(n_recommendations)
            
            # Convertir a formato de respuesta
            recommendations = [self._post_to_dict(post) for post in recommended_posts]
            
            # Guardar en caché
            self.user_based_recommendations_cache[user_id] = recommendations
            self.last_cache_update = datetime.datetime.now()
            
            return recommendations
        except Exception as e:
            logger.error(f"Error al obtener recomendaciones para el usuario {user_id}: {e}")
            # Fallback a posts populares en caso de error
            return self._get_popular_posts(n_recommendations)
    
    def get_similar_posts(self, post_id: int, n_recommendations: int = 5) -> List[Dict]:
        """
        Obtiene posts similares a un post dado
        
        Args:
            post_id (int): ID del post
            n_recommendations (int, optional): Número de recomendaciones. Default es 5.
            
        Returns:
            List[Dict]: Lista de posts similares
        """
        # Verificar si hay recomendaciones en caché
        if self._is_cache_valid() and post_id in self.similar_posts_cache:
            return self.similar_posts_cache[post_id][:n_recommendations]
        
        try:
            # Obtener el post
            post = self.db.query(Post).filter(Post.id == post_id).first()
            if not post:
                return []
            
            # Obtener todos los posts
            all_posts = self.db.query(Post).all()
            
            # Filtrar posts por categoría si está disponible
            if post.categorie:
                category_posts = [p for p in all_posts if p.categorie == post.categorie and p.id != post_id]
                if len(category_posts) >= n_recommendations:
                    # Si hay suficientes posts en la misma categoría, usarlos
                    similar_posts = category_posts[:n_recommendations]
                    result = [self._post_to_dict(p) for p in similar_posts]
                    self.similar_posts_cache[post_id] = result
                    return result
            
            # Si no hay suficientes posts en la misma categoría, usar similitud de contenido
            # Crear matriz de características (por ahora solo usamos categoría como característica)
            posts_df = pd.DataFrame({
                'id': [p.id for p in all_posts],
                'categorie': [p.categorie or "unknown" for p in all_posts]
            })
            
            # One-hot encoding de categorías
            categories_dummies = pd.get_dummies(posts_df['categorie'])
            
            # Calcular similitud
            post_idx = posts_df[posts_df['id'] == post_id].index[0]
            post_vector = categories_dummies.iloc[post_idx].values.reshape(1, -1)
            
            similarities = []
            for i, p_id in enumerate(posts_df['id']):
                if p_id != post_id:
                    other_vector = categories_dummies.iloc[i].values.reshape(1, -1)
                    sim = cosine_similarity(post_vector, other_vector)[0][0]
                    similarities.append((p_id, sim))
            
            # Ordenar por similitud
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Obtener los top n posts
            similar_post_ids = [s[0] for s in similarities[:n_recommendations]]
            
            # Obtener detalles de los posts
            similar_posts = []
            for similar_id in similar_post_ids:
                similar_post = self.db.query(Post).filter(Post.id == similar_id).first()
                if similar_post:
                    similar_posts.append(self._post_to_dict(similar_post))
            
            # Guardar en caché
            self.similar_posts_cache[post_id] = similar_posts
            self.last_cache_update = datetime.datetime.now()
            
            return similar_posts
        except Exception as e:
            logger.error(f"Error al obtener posts similares para el post {post_id}: {e}")
            return []
    
    def _get_popular_posts(self, n_posts: int = 5) -> List[Dict]:
        """
        Obtiene los posts más populares basados en likes y visitas
        
        Args:
            n_posts (int, optional): Número de posts a retornar. Default es 5.
            
        Returns:
            List[Dict]: Lista de posts populares
        """
        try:
            # Obtener posts con conteo de likes y visitas
            posts_with_stats = self.db.query(
                Post,
                func.count(Like.id).label('like_count'),
                func.count(Visit.id).label('visit_count')
            ).outerjoin(
                Like, Post.id == Like.post_id
            ).outerjoin(
                Visit, Post.id == Visit.post_id
            ).group_by(
                Post.id
            ).order_by(
                func.count(Like.id).desc(),
                func.count(Visit.id).desc()
            ).limit(n_posts).all()
            
            # Convertir a formato de respuesta
            popular_posts = []
            for post, _, _ in posts_with_stats:
                popular_posts.append(self._post_to_dict(post))
            
            return popular_posts
        except Exception as e:
            logger.error(f"Error al obtener posts populares: {e}")
            # Fallback: obtener los posts más recientes
            recent_posts = self.db.query(Post).order_by(Post.created_at.desc()).limit(n_posts).all()
            return [self._post_to_dict(post) for post in recent_posts]
    
    def _post_to_dict(self, post, current_user = None) -> Dict:
        """Convierte un objeto Post a un diccionario"""
        # Asegurar que el id esté presente y sea un entero
        post_id = post.id
        if post_id is None:
            logger.warning(f"Post sin ID encontrado: {post.title}")
            post_id = 0
            
        if current_user:
            post_isliked = self.db.query(models.Like).filter(
                models.Like.post_id == post.id,
                models.Like.user_id == current_user.id
            ).first() is not None
        else:
            post_isliked = False
        
        return {
            "id": post_id,
            "title": post.title,
            "content": post.content[:100] + "..." if len(post.content) > 100 else post.content,
            "image": post.image,
            "categorie": post.categorie,
            "likes": self.db.query(models.Like).filter(models.Like.post_id == post.id).count(),
            "visits": self.db.query(models.Visit).filter(models.Visit.post_id == post.id).count(),
            "isliked": post_isliked
        }
    
    def invalidate_cache(self):
        """Invalida el caché de recomendaciones"""
        self.user_based_recommendations_cache = {}
        self.content_based_recommendations_cache = {}
        self.similar_posts_cache = {}
        self.last_cache_update = datetime.datetime.now()
    
    def __del__(self):
        """Cierra la sesión de la base de datos al destruir el objeto"""
        self.db.close()

# Instancia global del sistema de recomendación
recommendation_system = RecommendationSystem()