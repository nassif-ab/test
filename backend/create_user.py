from database import SessionLocal
from crud import create_user
from schemas import UserCreate
from faker import Faker

fake = Faker()

def main():
    # Crear una sesión de base de datos
    db = SessionLocal()
    
    try:
        total_users = 300
        users_created = 0

        for _ in range(total_users):
            user_data = UserCreate(
                username=fake.user_name(),
                email=fake.unique.email(),
                password="123456789",
                is_admin=False
            )

            try:
                user = create_user(db, user_data)
                users_created += 1
                if users_created % 50 == 0:
                    print(f"✅ {users_created} usuarios creados...")
            except Exception as inner_error:
                print(f"⚠️ No se pudo crear un usuario: {inner_error}")
        
        db.commit()
        print(f"\n🎉 Total de usuarios creados: {users_created}")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
    
    finally:
        # Cerrar la sesión
        db.close()

if __name__ == "__main__":
    main()
