from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import schemas, crud, models
from database import SessionLocal
from typing import List, Dict, Any
from routers.posts import get_optional_user
from routers.auth import get_current_user
from datetime import datetime, timedelta

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

@router.get("/", response_model=list[schemas.UserOut])
def read_users(db: Session = Depends(get_db)):
    return crud.get_users(db)

@router.get("/{user_id}/stats")
def get_user_stats(user_id: int, db: Session = Depends(get_db), current_user = Depends(get_optional_user)):
    # Verificar que el usuario existe
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Obtener total de posts del usuario
    total_posts = db.query(models.Post).filter(models.Post.user_id == user_id).count()
    
    # Obtener total de likes dados por el usuario
    total_likes = db.query(models.Like).filter(models.Like.user_id == user_id).count()
    
    # Obtener total de visitas del usuario
    total_visits = db.query(models.Visit).filter(models.Visit.user_id == user_id).count()
    
    # Obtener categorías favoritas (basado en likes y visitas)
    # Primero, obtenemos los posts que el usuario ha dado like
    liked_posts = db.query(models.Post).join(models.Like, models.Like.post_id == models.Post.id)\
                    .filter(models.Like.user_id == user_id).all()
    
    # Luego, obtenemos los posts que el usuario ha visitado
    visited_posts = db.query(models.Post).join(models.Visit, models.Visit.post_id == models.Post.id)\
                    .filter(models.Visit.user_id == user_id).all()
    
    # Combinamos ambos conjuntos de posts
    all_interaction_posts = liked_posts + visited_posts
    
    # Contamos las categorías
    category_counts = {}
    for post in all_interaction_posts:
        if post.categorie:
            if post.categorie in category_counts:
                category_counts[post.categorie] += 1
            else:
                category_counts[post.categorie] = 1
    
    # Convertimos a lista de diccionarios y ordenamos por conteo
    favorite_categories = [{'category': cat, 'count': count} for cat, count in category_counts.items()]
    favorite_categories.sort(key=lambda x: x['count'], reverse=True)
    
    return {
        "user_id": user_id,
        "username": user.username,
        "total_posts": total_posts,
        "total_likes": total_likes,
        "total_visits": total_visits,
        "favorite_categories": favorite_categories
    }

@router.get("/analytics/power-bi")
def get_global_analytics_data(api_key: str = None, db: Session = Depends(get_db)):
    # Verificar la clave API (una clave simple para demostración)
    # En producción, deberías usar un sistema más seguro de gestión de claves API
    if api_key == "pfe2025_test":
        # Si la clave API es correcta, permitir acceso
        pass
    else:
        # Si no hay clave API válida, rechazar acceso
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Provide a valid API key using ?api_key=*********"
        )
    """Proporciona datos globales para análisis en Power BI"""
    
    # Datos de usuarios
    users_data = []
    users = db.query(models.User).all()
    for user in users:
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin,
            "created_at": user.created_at,
            "posts_count": db.query(models.Post).filter(models.Post.user_id == user.id).count(),
            "likes_given": db.query(models.Like).filter(models.Like.user_id == user.id).count(),
            "visits_count": db.query(models.Visit).filter(models.Visit.user_id == user.id).count()
        }
        users_data.append(user_data)
    
    # Datos de publicaciones
    posts_data = []
    posts = db.query(models.Post).all()
    for post in posts:
        post_data = {
            "id": post.id,
            "title": post.title,
            "content": post.content[:100] + "..." if post.content and len(post.content) > 100 else post.content,
            "categorie": post.categorie,
            "user_id": post.user_id,
            "created_at": post.created_at,
            "likes_count": db.query(models.Like).filter(models.Like.post_id == post.id).count(),
            "visits_count": db.query(models.Visit).filter(models.Visit.post_id == post.id).count()
        }
        posts_data.append(post_data)
    
    # Datos de interacciones (likes)
    likes_data = []
    likes = db.query(models.Like).all()
    for like in likes:
        like_data = {
            "id": like.id,
            "user_id": like.user_id,
            "post_id": like.post_id,
            "created_at": like.created_at
        }
        likes_data.append(like_data)
    
    # Datos de visitas
    visits_data = []
    visits = db.query(models.Visit).all()
    for visit in visits:
        visit_data = {
            "id": visit.id,
            "user_id": visit.user_id,
            "post_id": visit.post_id,
            "ip_address": visit.ip_address,
            "visit_date": visit.visit_date
        }
        visits_data.append(visit_data)
    
    # Estadísticas por categoría
    category_stats = db.query(
        models.Post.categorie,
        func.count(models.Post.id).label('post_count'),
        func.count(models.Like.id).label('like_count'),
        func.count(models.Visit.id).label('visit_count')
    ).outerjoin(models.Like, models.Like.post_id == models.Post.id)\
     .outerjoin(models.Visit, models.Visit.post_id == models.Post.id)\
     .filter(models.Post.categorie != None)\
     .group_by(models.Post.categorie)\
     .all()
    
    categories_data = []
    for cat, post_count, like_count, visit_count in category_stats:
        cat_data = {
            "categorie": cat,
            "post_count": post_count,
            "like_count": like_count,
            "visit_count": visit_count,
            "engagement_rate": (like_count + visit_count) / post_count if post_count > 0 else 0
        }
        categories_data.append(cat_data)
    
    # Actividad por tiempo
    # Últimos 30 días
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    daily_activity = []
    for i in range(30):
        date = thirty_days_ago + timedelta(days=i)
        next_date = date + timedelta(days=1)
        
        posts_count = db.query(models.Post)\
                      .filter(models.Post.created_at >= date, models.Post.created_at < next_date)\
                      .count()
        
        likes_count = db.query(models.Like)\
                      .filter(models.Like.created_at >= date, models.Like.created_at < next_date)\
                      .count()
        
        visits_count = db.query(models.Visit)\
                       .filter(models.Visit.visit_date >= date, models.Visit.visit_date < next_date)\
                       .count()
        
        daily_activity.append({
            "date": date.strftime("%Y-%m-%d"),
            "posts_count": posts_count,
            "likes_count": likes_count,
            "visits_count": visits_count,
            "total_activity": posts_count + likes_count + visits_count
        })
    
    return {
        "users": users_data,
        "posts": posts_data,
        "likes": likes_data,
        "visits": visits_data,
        "categories": categories_data,
        "daily_activity": daily_activity,
        "total_users": len(users_data),
        "total_posts": len(posts_data),
        "total_likes": len(likes_data),
        "total_visits": len(visits_data),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
