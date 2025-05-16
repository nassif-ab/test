from sqlalchemy.orm import Session
import models, schemas

# ====== USERS ======
def create_user(db: Session, user: schemas.UserCreate):
    # تشفير كلمة المرور قبل حفظها
    hashed_password = get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        fullName=user.fullName,
        email=user.email,
        password=hashed_password,  # كلمة المرور مشفرة الآن
        is_admin=user.is_admin  # Asignar el valor de is_admin del esquema
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_users(db: Session):
    return db.query(models.User).all()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# ====== POSTS ======
def create_post(db: Session, post: schemas.PostCreate, user_id: int):
    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=user_id,
        image=post.image,
        categorie=post.categorie
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

def get_posts(db: Session, current_user_id=None):
    posts = db.query(models.Post).all()
    result = []
    
    # Crear un diccionario con los datos del post y añadir información de likes y visitas
    for post in posts:
        # Crear un diccionario con los atributos del post
        post_dict = {
            "id": post.id,
            "user_id": post.user_id,
            "title": post.title,
            "content": post.content,
            "categorie": post.categorie,
            "image": post.image,
            "created_at": post.created_at,
            # Contar el número total de likes
            "likes": db.query(models.Like).filter(models.Like.post_id == post.id).count(),
            # Contar el número total de visitas
            "visits": db.query(models.Visit).filter(models.Visit.post_id == post.id).count()
        }
        
        # Verificar si el usuario actual ha dado like (si se proporciona un ID de usuario)
        if current_user_id:
            post_dict["isliked"] = db.query(models.Like).filter(
                models.Like.post_id == post.id,
                models.Like.user_id == current_user_id
            ).first() is not None
        else:
            post_dict["isliked"] = False
        
        result.append(post_dict)
    
    return result

def get_user_posts(db: Session, user_id: int):
    posts = db.query(models.Post).filter(models.Post.user_id == user_id).all()
    result = []
    
    # Crear un diccionario con los datos del post y añadir información de likes y visitas
    for post in posts:
        # Crear un diccionario con los atributos del post
        post_dict = {
            "id": post.id,
            "user_id": post.user_id,
            "title": post.title,
            "content": post.content,
            "categorie": post.categorie,
            "image": post.image,
            "created_at": post.created_at,
            # Contar el número total de likes
            "likes": db.query(models.Like).filter(models.Like.post_id == post.id).count(),
            # Contar el número total de visitas
            "visits": db.query(models.Visit).filter(models.Visit.post_id == post.id).count()
        }
        
        # El usuario actual es el propietario, por lo que podemos verificar si ha dado like
        post_dict["isliked"] = db.query(models.Like).filter(
            models.Like.post_id == post.id,
            models.Like.user_id == user_id
        ).first() is not None
        
        result.append(post_dict)
    
    return result

# ====== LIKES ======
def add_like(db: Session, user_id: int, post_id: int):
    # Crear nuevo like
    like = models.Like(user_id=user_id, post_id=post_id)
    db.add(like)
    db.commit()
    db.refresh(like)
    
    # Actualizar recomendaciones para este usuario
    try:
        from RecommendationSystem import recommendation_system
        # Invalidar el caché para este usuario
        if user_id in recommendation_system.user_based_recommendations_cache:
            del recommendation_system.user_based_recommendations_cache[user_id]
        # Actualizar la fecha de última actualización del caché
        import datetime
        recommendation_system.last_cache_update = datetime.datetime.now()
    except Exception as e:
        print(f"Error al actualizar recomendaciones después de like: {e}")
    
    return like

# ====== VISITS ======
def record_visit(db: Session, post_id: int, user_id: int = None, ip_address: str = None):
    # Verificar si el post existe
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        return None
    
    # Crear una nueva visita
    visit = models.Visit(post_id=post_id, user_id=user_id, ip_address=ip_address)
    db.add(visit)
    db.commit()
    db.refresh(visit)
    
    # Actualizar recomendaciones para este usuario si está autenticado
    if user_id:
        try:
            from RecommendationSystem import recommendation_system
            # Invalidar el caché para este usuario
            if user_id in recommendation_system.user_based_recommendations_cache:
                del recommendation_system.user_based_recommendations_cache[user_id]
            # Actualizar la fecha de última actualización del caché
            import datetime
            recommendation_system.last_cache_update = datetime.datetime.now()
        except Exception as e:
            print(f"Error al actualizar recomendaciones después de visita: {e}")
    
    # Actualizar recomendaciones similares para este post
    try:
        from RecommendationSystem import recommendation_system
        # Invalidar el caché para este post
        if post_id in recommendation_system.similar_posts_cache:
            del recommendation_system.similar_posts_cache[post_id]
    except Exception as e:
        print(f"Error al actualizar posts similares después de visita: {e}")
    
    return visit

def get_post_visits_count(db: Session, post_id: int):
    # Contar el número total de visitas para un post
    return db.query(models.Visit).filter(models.Visit.post_id == post_id).count()

def get_user_visits(db: Session, user_id: int):
    # Obtener todas las visitas de un usuario
    return db.query(models.Visit).filter(models.Visit.user_id == user_id).all()

# crud.py (إضافة إلى الملف الحالي)
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user
def authenticate_admin(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    # Verificar que el usuario tenga el rol de administrador
    # Imprimir información para depuración
    print(f"Usuario: {user.username}, is_admin: {user.is_admin}, tipo: {type(user.is_admin)}")
    # Comprobar si el usuario es administrador (is_admin=True)
    if not user.is_admin:
        return False
    return user