
data_users=[
  {
    "fullName": "Youssef El Amrani",
    "email": "youssef.elamrani@gmail.com",
    "username": "y.elamrani"
  },
  {
    "fullName": "Fatima Zahra Bouziane",
    "email": "fatimaz.bouziane@gmail.com",
    "username": "f.bouziane"
  },
  {
    "fullName": "Mohamed Berrada",
    "email": "mohamed.berrada@gmail.com",
    "username": "m.berrada"
  },
  {
    "fullName": "Khadija El Khalfi",
    "email": "khadija.elkhalfi@gmail.com",
    "username": "k.elkhalfi"
  },
  {
    "fullName": "Rachid Ait El Caid",
    "email": "rachid.aitelcaid@gmail.com",
    "username": "r.aitelcaid"
  },
  {
    "fullName": "Laila Idrissi",
    "email": "laila.idrissi@gmail.com",
    "username": "l.idrissi"
  },
  {
    "fullName": "Hamza El Fassi",
    "email": "hamza.elfassi@gmail.com",
    "username": "h.elfassi"
  },
  {
    "fullName": "Salma Benali",
    "email": "salma.benali@gmail.com",
    "username": "s.benali"
  },
  {
    "fullName": "Ahmed Chafik",
    "email": "ahmed.chafik@gmail.com",
    "username": "a.chafik"
  },
  {
    "fullName": "Imane Karimi",
    "email": "imane.karimi@gmail.com",
    "username": "i.karimi"
  },
  {
    "fullName": "Soufiane El Ghazali",
    "email": "soufiane.elghazali@gmail.com",
    "username": "s.elghazali"
  },
  {
    "fullName": "Nisrine Bakkali",
    "email": "nisrine.bakkali@gmail.com",
    "username": "n.bakkali"
  },
  {
    "fullName": "Anas Ouchen",
    "email": "anas.ouchen@gmail.com",
    "username": "a.ouchen"
  },
  {
    "fullName": "Zineb El Arabi",
    "email": "zineb.elarabi@gmail.com",
    "username": "z.elarabi"
  },
  {
    "fullName": "Othmane El Yousfi",
    "email": "othmane.elyousfi@gmail.com",
    "username": "o.elyousfi"
  },
  {
    "fullName": "Najat Touil",
    "email": "najat.touil@gmail.com",
    "username": "n.touil"
  },
  {
    "fullName": "Walid Amzil",
    "email": "walid.amzil@gmail.com",
    "username": "w.amzil"
  },
  {
    "fullName": "Sara Bennani",
    "email": "sara.bennani@gmail.com",
    "username": "s.bennani"
  },
  {
    "fullName": "Mehdi Bouazzaoui",
    "email": "mehdi.bouazzaoui@gmail.com",
    "username": "m.bouazzaoui"
  },
  {
    "fullName": "Hajar El Idrissi",
    "email": "hajar.elidrissi@gmail.com",
    "username": "h.elidrissi"
  }
]






from database import SessionLocal
from sqlalchemy.orm import Session
from crud import create_user, get_user_by_username, get_user_by_email
from schemas import UserCreate
from models import User

def create_or_update_user(db: Session, user_data: dict):
    # Verificar si el usuario ya existe por nombre de usuario o email
    existing_user_by_username = get_user_by_username(db, user_data["username"])
    existing_user_by_email = get_user_by_email(db, user_data["email"])
    
    if existing_user_by_username or existing_user_by_email:
        # El usuario ya existe, actualizar sus datos
        existing_user = existing_user_by_username or existing_user_by_email
        print(f"Usuario {user_data['username']} ya existe con ID: {existing_user.id}, actualizando datos...")
        
        # Actualizar los campos del usuario
        existing_user.username = user_data["username"]
        existing_user.fullName = user_data["fullName"]
        existing_user.email = user_data["email"]
        
        # Guardar los cambios
        db.commit()
        db.refresh(existing_user)
        
        return existing_user, "actualizado"
    else:
        # El usuario no existe, crearlo
        user_create = UserCreate(
            username=user_data["username"],
            fullName=user_data["fullName"],
            email=user_data["email"],
            password=user_data["password"],
            is_admin=user_data.get("is_admin", False)
        )
        
        new_user = create_user(db, user_create)
        return new_user, "creado"

def main():
    # Crear una sesión de base de datos
    db = SessionLocal()
    ids=[]
    try:
        # Procesar cada usuario en la lista
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
            print(f"✅ Usuario {action} con ID: {user.id}, username: {user.username}")
            ids.append(user.id)
        
    except Exception as e:
        print(f"❌ Error al crear el usuario: {e}")
    
    finally:
        # Cerrar la sesión
        db.close()

if __name__ == "__main__":
    main()
