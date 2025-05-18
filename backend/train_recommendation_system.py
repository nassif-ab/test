import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Dict

# Importar modelos y sistema de recomendación
from models import User, Post, Like, Visit
from database import SessionLocal, engine, Base
from RecommendationSystem import recommendation_system

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_recommendations():
    """
    Probar el sistema de recomendación con los datos de muestra
    """
    # Crear una sesión de base de datos
    db = SessionLocal()
    
    # Obtener todos los usuarios
    users = db.query(User).all()
    
    # Forzar el entrenamiento ignorando el tiempo del caché
    recommendation_system.cache_expiry = timedelta(minutes=0)
    recommendation_system.last_cache_update = datetime.min
    recommendation_system.invalidate_cache()
    
    # Probar recomendaciones para cada usuario
    for user in users:
        logger.info(f"\n=== Recomendaciones para el usuario {user.username} (ID: {user.id}) ===")
        
        # Obtener likes del usuario
        likes = db.query(Like).filter(Like.user_id == user.id).all()
        liked_posts = db.query(Post).filter(Post.id.in_([like.post_id for like in likes])).all()
        
        logger.info(f"Posts que le gustan a {user.username}:")
        for post in liked_posts:
            logger.info(f"- {post.title} (Categoría: {post.categorie})")
        
        # Obtener recomendaciones para el usuario
        recommendations = recommendation_system.get_recommendations_for_user(user.id, n_recommendations=5)
        
        logger.info(f"\nRecomendaciones para {user.username}:")
        for i, rec in enumerate(recommendations):
            logger.info(f"{i+1}. {rec['title']} (Categoría: {rec['categorie']})")
        
        # Probar recomendaciones similares para un post específico
        if liked_posts:
            sample_post = liked_posts[0]
            logger.info(f"\nPosts similares a '{sample_post.title}':")
            similar_posts = recommendation_system.get_similar_posts(sample_post.id, n_recommendations=3)
            
            for i, rec in enumerate(similar_posts):
                logger.info(f"{i+1}. {rec['title']} (Categoría: {rec['categorie']})")
    
    db.close()

def main():
    # Probar el sistema de recomendación con los datos existentes
    logger.info("Iniciando prueba del sistema de recomendación con datos existentes...")
    
    # Invalidar el caché para asegurar recomendaciones actualizadas
    recommendation_system.invalidate_cache()
    
    # Probar el sistema de recomendación
    test_recommendations()
    
    logger.info("\nPrueba del sistema de recomendación completada.")
    logger.info("Las recomendaciones ahora estarán actualizadas en la aplicación.")
    logger.info("Puedes probar las recomendaciones en la interfaz de usuario.")
    logger.info("Recuerda que las recomendaciones mejoran con más interacciones de usuarios.")
    logger.info("Cuantos más likes y visitas haya, mejores serán las recomendaciones.")

if __name__ == "__main__":
    main()
