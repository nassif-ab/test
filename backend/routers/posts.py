# routers/posts.py (تحديث)
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import schemas, crud, models  # Importar models
from database import SessionLocal
from routers.auth import get_current_user, SECRET_KEY, ALGORITHM  # استيراد دالة التحقق من المستخدم والمتغيرات اللازمة

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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