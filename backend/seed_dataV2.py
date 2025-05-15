import os
import json
from sqlalchemy.orm import Session
from models import Post
from crud import create_post
from schemas import PostCreate
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
    for article in articles:
        try:
            post_data = PostCreate(
                titre=article["titre"],
                image=article["image"],
                contenu=markdown.markdown(article["contenu"]),
                categorie=article["categorie"]
            )
            create_post(db, post_data)
            print(f"✅ Article ajouté : {article['titre']}")
        except Exception as e:
            print(f"❌ Erreur pour l'article '{article.get('titre', 'inconnu')}': {e}")


def main():
    db = SessionLocal()
    articles = load_articles_from_json(ARTICLE_DIR)
    seed_articles(db, articles)
    db.close()

if __name__ == "__main__":
    main()
