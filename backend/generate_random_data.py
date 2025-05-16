import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from crud import get_users, get_user_by_username, get_user_by_email, create_user
from schemas import UserCreate
import time

# Importar datos de usuarios del archivo data_users.py
from data_users import data_users, create_or_update_user

def get_random_date(start_date, end_date):
    """Genera una fecha aleatoria entre start_date y end_date"""
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)

def generate_random_visits(db: Session, num_visits: int = 500, start_date=None, end_date=None):
    """Genera visitas aleatorias para los posts"""
    print("Generando visitas aleatorias...")
    
    # Obtener todos los usuarios y posts
    users = db.query(models.User).all()
    posts = db.query(models.Post).all()
    
    if not users or not posts:
        print("No hay usuarios o posts para generar visitas")
        return
    
    # Si no se especifican fechas, usar los últimos 6 meses
    if start_date is None:
        start_date = datetime.now() - timedelta(days=180)
    if end_date is None:
        end_date = datetime.now()
        
    print(f"Generando visitas entre {start_date.strftime('%Y-%m-%d')} y {end_date.strftime('%Y-%m-%d')}...")
    
    # Generar visitas aleatorias
    visits_created = 0
    for _ in range(num_visits):
        # Algunos visitantes serán anónimos (sin user_id)
        is_anonymous = random.random() < 0.3  # 30% de probabilidad de ser anónimo
        
        # Seleccionar un post aleatorio
        post = random.choice(posts)
        
        # Crear la visita
        visit = models.Visit(
            post_id=post.id,
            user_id=None if is_anonymous else random.choice(users).id,
            ip_address=f"192.168.1.{random.randint(1, 255)}",
            visit_date=get_random_date(start_date, end_date)
        )
        
        db.add(visit)
        visits_created += 1
        
        # Commit cada 100 registros para evitar problemas de memoria
        if visits_created % 100 == 0:
            db.commit()
            print(f"  {visits_created} visitas creadas...")
    
    db.commit()
    print(f"✅ {visits_created} visitas aleatorias generadas")

def generate_random_likes(db: Session, num_likes: int = 300, start_date=None, end_date=None):
    """Genera likes aleatorios para los posts"""
    print("Generando likes aleatorios...")
    
    # Obtener todos los usuarios y posts
    users = db.query(models.User).all()
    posts = db.query(models.Post).all()
    
    if not users or not posts:
        print("No hay usuarios o posts para generar likes")
        return
    
    # Si no se especifican fechas, usar los últimos 6 meses
    if start_date is None:
        start_date = datetime.now() - timedelta(days=180)
    if end_date is None:
        end_date = datetime.now()
        
    print(f"Generando likes entre {start_date.strftime('%Y-%m-%d')} y {end_date.strftime('%Y-%m-%d')}...")
    
    # Conjunto para evitar duplicados (un usuario no puede dar like más de una vez al mismo post)
    existing_likes = set()
    
    # Obtener likes existentes para evitar duplicados
    likes = db.query(models.Like).all()
    for like in likes:
        existing_likes.add((like.user_id, like.post_id))
    
    # Generar likes aleatorios
    likes_created = 0
    attempts = 0
    max_attempts = num_likes * 2  # Limitar intentos para evitar bucles infinitos
    
    while likes_created < num_likes and attempts < max_attempts:
        attempts += 1
        
        # Seleccionar un usuario y post aleatorio
        user = random.choice(users)
        post = random.choice(posts)
        
        # Verificar si ya existe este like
        if (user.id, post.id) in existing_likes:
            continue
        
        # Crear el like
        like = models.Like(
            user_id=user.id,
            post_id=post.id,
            created_at=get_random_date(start_date, end_date)
        )
        
        db.add(like)
        existing_likes.add((user.id, post.id))
        likes_created += 1
        
        # Commit cada 100 registros para evitar problemas de memoria
        if likes_created % 100 == 0:
            db.commit()
            print(f"  {likes_created} likes creados...")
    
    db.commit()
    print(f"✅ {likes_created} likes aleatorios generados")

def create_users_from_data(db: Session):
    """Crea o actualiza usuarios desde los datos importados"""
    print("Creando o actualizando usuarios...")
    
    users_created = 0
    users_updated = 0
    
    for data in data_users:
        user_data = {
            "username": data["username"],
            "fullName": data["fullName"],
            "email": data["email"],
            "password": "123456789",
            "is_admin": False
        }
        
        # Crear o actualizar el usuario
        user, action = create_or_update_user(db, user_data)
        
        if action == "creado":
            users_created += 1
        else:
            users_updated += 1
    
    print(f"✅ {users_created} usuarios creados y {users_updated} usuarios actualizados")

def main():
    # Crear una sesión de base de datos
    db = SessionLocal()
    
    try:
        # Definir rango de fechas personalizado (últimos 3 meses por defecto)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)  # 3 meses
        
        # Permitir personalizar el rango de fechas desde la línea de comandos
        import sys
        if len(sys.argv) > 2:
            try:
                # Formato esperado: YYYY-MM-DD
                start_date = datetime.strptime(sys.argv[1], "%Y-%m-%d")
                end_date = datetime.strptime(sys.argv[2], "%Y-%m-%d")
                print(f"Usando rango de fechas personalizado: {start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}")
            except ValueError:
                print("Formato de fecha incorrecto. Usando valores predeterminados.")
                print("Formato correcto: python generate_random_data.py 2025-01-01 2025-05-01")
        
        # Primero crear o actualizar los usuarios
        create_users_from_data(db)
        
        # Luego generar datos aleatorios con el rango de fechas especificado
        generate_random_visits(db, num_visits=1000, start_date=start_date, end_date=end_date)
        generate_random_likes(db, num_likes=500, start_date=start_date, end_date=end_date)
        
        # Entrenar el sistema de recomendación
        print("\nDatos aleatorios generados con éxito.")
        print("Para mejorar las recomendaciones, ejecute el script de entrenamiento:")
        print("  python scheduled_training.py")
        
    except Exception as e:
        print(f"❌ Error al generar datos aleatorios: {e}")
    
    finally:
        # Cerrar la sesión
        db.close()

if __name__ == "__main__":
    main()
