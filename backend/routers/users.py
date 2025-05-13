from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import schemas, crud, models
from database import SessionLocal
from typing import List, Dict
from routers.posts import get_optional_user

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
