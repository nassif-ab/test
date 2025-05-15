from database import SessionLocal
from crud import create_user
from schemas import UserCreate

def main():
    # Crear una sesión de base de datos
    db = SessionLocal()
    
    try:
        # Crear un usuario de prueba
        user_data = UserCreate(
            username="admin",
            email="admin@example.com",
            password="123456789",
            is_admin=True
        )
        
        # Crear el usuario en la base de datos
        user = create_user(db, user_data)
        print(f"✅ Usuario creado con ID: {user.id}")
        
    except Exception as e:
        print(f"❌ Error al crear el usuario: {e}")
    
    finally:
        # Cerrar la sesión
        db.close()

if __name__ == "__main__":
    main()
