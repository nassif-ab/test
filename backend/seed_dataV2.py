import os
import json
from sqlalchemy.orm import Session
from models import Post
import crud
from schemas import PostCreate, UserCreate
from database import SessionLocal
import markdown

# Dossier des fichiers JSON générés
ARTICLE_DIR = "generated_articles"

def load_articles_from_json(directory):
    articles = []
    for filename in os.listdir(directory):
        if filename.endswith(".json") and not filename.endswith("_error.json"):
            path = os.path.join(directory, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    articles.append(data)
            except Exception as e:
                print(f"❌ Erreur lors du chargement de {filename} : {e}")
    return articles

def seed_articles(db: Session, articles):

    admin_id = get_admin_id_or_create(db)

    for article in articles:
        try:
            post_data = PostCreate(
                title=article["titre"],  # Cambiar titre a title
                image=article["image"],
                content=markdown.markdown(article["contenu"]),  # Cambiar contenu a content
                categorie=article["categorie"]
            )
            crud.create_post(db, post_data, user_id=admin_id)  # Añadir user_id=1 o el ID de un usuario existente
            print(f"✅ Article ajouté : {article['titre']}")
        except Exception as e:
            print(f"❌ Erreur pour l'article '{article.get('titre', 'inconnu')}': {e}")

def get_admin_id_or_create(db: Session):
    # Buscar usuario admin existente
    admin = crud.get_user_by_username(db, username="admin")
    if admin:
        return admin.id
    else:
        # Crear usuario admin si no existe
        user_data = UserCreate(
            username="admin",
            fullName="admin",
            email="admin@example.com",
            password="123456789",
            is_admin=True
        )
        new_admin = crud.create_user(db, user_data)
        return new_admin.id
def main():
    db = SessionLocal()
    articles = load_articles_from_json(ARTICLE_DIR)
    seed_articles(db, articles)
    db.close()

if __name__ == "__main__":
    main()
