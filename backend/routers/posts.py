# routers/posts.py (تحديث)
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict
import schemas, crud, models  # Importar models
from database import SessionLocal, get_db
from routers.auth import get_current_user, SECRET_KEY, ALGORITHM  # استيراد دالة التحقق من المستخدم والمتغيرات اللازمة

router = APIRouter()

@router.post("/", response_model=schemas.PostOut)
def create_post(
    post: schemas.PostCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # إضافة التحقق من المستخدم
):
    return crud.create_post(db, post, current_user.id)

from fastapi.security import OAuth2PasswordBearer
from fastapi import Security, HTTPException, status
from jose import JWTError, jwt
from typing import Optional

# Definir una versión opcional del get_current_user
async def get_optional_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="api/auth/token", auto_error=False)), db: Session = Depends(get_db)):
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = schemas.TokenData(username=username)
    except JWTError:
        return None
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        return None
    return user

@router.get("/", response_model=list[schemas.PostOut])
def read_posts(db: Session = Depends(get_db), current_user = Depends(get_optional_user)):
    # Si el usuario está autenticado, pasar su ID para verificar sus likes
    current_user_id = current_user.id if current_user else None
    return crud.get_posts(db, current_user_id)

@router.get("/my-posts", response_model=list[schemas.PostOut])
def read_my_posts(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # إضافة التحقق من المستخدم
):
    return crud.get_posts(db, current_user.id)

# Endpoint para obtener estadísticas generales de publicaciones
@router.get("/stats", response_model=Dict)
def get_post_stats(db: Session = Depends(get_db), current_user = Depends(get_optional_user)):
    """Obtiene estadísticas generales de todas las publicaciones"""
    
    # Total de posts
    total_posts = db.query(models.Post).count()
    
    # Total de likes
    total_likes = db.query(models.Like).count()
    
    # Total de visitas
    total_visits = db.query(models.Visit).count()
    
    # Categorías populares
    categories = db.query(models.Post.categorie, func.count(models.Post.id).label('count'))\
                .filter(models.Post.categorie != None)\
                .group_by(models.Post.categorie)\
                .order_by(func.count(models.Post.id).desc())\
                .all()
    
    popular_categories = [{'category': cat, 'count': count} for cat, count in categories]
    
    # Posts más populares por likes
    most_liked_posts_query = db.query(models.Post, func.count(models.Like.id).label('like_count'))\
                            .join(models.Like, models.Like.post_id == models.Post.id, isouter=True)\
                            .group_by(models.Post.id)\
                            .order_by(func.count(models.Like.id).desc())\
                            .limit(5)
    
    most_liked_posts = []
    for post, like_count in most_liked_posts_query:
        post_dict = {
            "id": str(post.id),
            "title": post.title,
            "content": post.content,
            "categorie": post.categorie,
            "image": post.image,
            "likes": like_count,
            "visits": db.query(models.Visit).filter(models.Visit.post_id == post.id).count()
        }
        most_liked_posts.append(post_dict)
    
    # Posts más visitados
    most_visited_posts_query = db.query(models.Post, func.count(models.Visit.id).label('visit_count'))\
                            .join(models.Visit, models.Visit.post_id == models.Post.id, isouter=True)\
                            .group_by(models.Post.id)\
                            .order_by(func.count(models.Visit.id).desc())\
                            .limit(5)
    
    most_visited_posts = []
    for post, visit_count in most_visited_posts_query:
        post_dict = {
            "id": str(post.id),
            "title": post.title,
            "content": post.content,
            "categorie": post.categorie,
            "image": post.image,
            "likes": db.query(models.Like).filter(models.Like.post_id == post.id).count(),
            "visits": visit_count
        }
        most_visited_posts.append(post_dict)
    
    return {
        "total_posts": total_posts,
        "total_likes": total_likes,
        "total_visits": total_visits,
        "popular_categories": popular_categories,
        "most_liked_posts": most_liked_posts,
        "most_visited_posts": most_visited_posts
    }

@router.get("/{post_id}", response_model=schemas.PostOut)
def read_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    # Verificar si el post existe
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Crear un diccionario con los datos del post
    post_dict = {
        "id": post.id,
        "user_id": post.user_id,
        "title": post.title,
        "content": post.content,
        "image": post.image,
        "created_at": post.created_at,
        # Contar el número total de likes
        "likes": db.query(models.Like).filter(models.Like.post_id == post.id).count(),
        # Contar el número total de visitas
        "visits": db.query(models.Visit).filter(models.Visit.post_id == post.id).count()
    }
    
    # Verificar si el usuario actual ha dado like (si está autenticado)
    if current_user:
        post_dict["isliked"] = db.query(models.Like).filter(
            models.Like.post_id == post.id,
            models.Like.user_id == current_user.id
        ).first() is not None
    else:
        post_dict["isliked"] = False
    
    return post_dict

@router.post("/{post_id}/like", response_model=schemas.LikeOut)
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Verificar si el post existe
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Verificar si el usuario ya ha dado like al post
    existing_like = db.query(models.Like).filter(
        models.Like.post_id == post_id,
        models.Like.user_id == current_user.id
    ).first()
    
    if existing_like:
        # Si ya existe un like, lo eliminamos (toggle)
        db.delete(existing_like)
        db.commit()
        
        # Crear un objeto que cumpla con el esquema LikeOut
        from datetime import datetime
        return schemas.LikeOut(
            id=0,
            user_id=current_user.id,
            post_id=post_id,
            created_at=datetime.now()  # Usar la fecha actual en lugar de None
        )
    else:
        # Si no existe, creamos un nuevo like
        return crud.add_like(db, current_user.id, post_id)

@router.post("/{post_id}/visit", response_model=schemas.VisitOut)
def record_visit(
    post_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    # Obtener la dirección IP del cliente
    client_ip = request.client.host if request.client else None
    
    # Si el usuario está autenticado, registrar la visita con su ID
    if current_user:
        return crud.record_visit(db, post_id, current_user.id, client_ip)
    else:
        # Si es un visitante anónimo, registrar solo la IP
        return crud.record_visit(db, post_id, None, client_ip)

@router.get("/{post_id}/visits", response_model=int)
def get_post_visits(
    post_id: int,
    db: Session = Depends(get_db)
):
    # Verificar si el post existe
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Devolver el número de visitas
    return crud.get_post_visits_count(db, post_id)

import models
from models import User
from RecommendationSystem import recommendation_system
from routers.auth import get_current_user

# Endpoint para obtener recomendaciones para un usuario
@router.get("/user/{user_id}/recommendations", response_model=List[schemas.PostBase])
def get_recommendations_for_user(user_id: int, n_recommendations: int = 5, db: Session = Depends(get_db)):
    """Obtiene recomendaciones de posts para un usuario específico"""
    print(f"Obteniendo recomendaciones para el usuario {user_id}")
    
    # Obtener recomendaciones
    recommendations = recommendation_system.get_recommendations_for_user(user_id, n_recommendations)
    
    print(f"Se encontraron {len(recommendations)} recomendaciones")
    return recommendations

# Endpoint para obtener posts similares a un post específico
@router.get("/{post_id}/similar", response_model=List[schemas.PostBase])
def get_similar_posts(post_id: int, n_recommendations: int = 5, db: Session = Depends(get_db)):
    """Obtiene posts similares a un post específico"""
    print(f"Obteniendo posts similares al post {post_id}")
    similar_posts = recommendation_system.get_similar_posts(post_id, n_recommendations)
    print(f"Se encontraron {len(similar_posts)} posts similares")
    return similar_posts