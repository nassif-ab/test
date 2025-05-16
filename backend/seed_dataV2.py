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
def get_image_name(nom_filiere: str) -> str:
    mapping = {
        "Génie Informatique": "genie-informatique.jpg",
        "Génie Électrique": "genie-electrique.jpg",
        "Génie Industriel": "genie-industriel.jpg",
        "Génie Mécatronique": "genie-mecatronique.jpg",
        "Réseaux et Systèmes de Télécommunications": "reseaux-telecommunications.jpg",
        "Efficacité Énergétique et Bâtiment Intelligent": "efficacite-energetique-batiment.jpg",
        "Génie Civil": "genie-civil.jpg",
        "Sécurité des Systèmes d’Information": "securite-systemes-information.jpg",
        "Intelligence Artificielle et IoT pour l’Industrie 4.0": "ia-iot-industrie4.jpg",
        "Management de la Supply Chain": "management-supply-chain.jpg",
        "Génie Mécanique et Aéronautique": "genie-mecanique-aeronautique.jpg",
        "Génie Électrique et Énergies Renouvelables": "genie-electrique-energies.jpg",
        "Licence en Génie Industriel": "licence-genie-industriel.jpg",
         # Nouvelles catégories
        "Big Data et Analytics": "big-data-analytics.jpg",
        "Développement Logiciel": "developpement-logiciel.jpg",
        "DevOps et CI/CD": "devops-cicd.jpg",
        "Blockchain et Technologies Distribuées": "blockchain-technologies.jpg",
        "Cybersécurité Offensive et Défensive": "cybersecurite.jpg",
        "Systèmes Embarqués et IoT": "systemes-embarques-iot.jpg",
        "Cloud Computing et Virtualisation": "cloud-computing.jpg",
        "Réalité Virtuelle et Augmentée": "realite-virtuelle-augmentee.jpg",
        "Intelligence Artificielle et Data Science": "ia-data-science.jpg",
        "Robotique Avancée": "robotique-avancee.jpg",
        "Biotechnologie et Ingénierie Biomédicale": "biotechnologie-biomedicale.jpg",
        "Gestion de Projets Technologiques": "gestion-projets-tech.jpg",
        "Design de l'Expérience Utilisateur (UX/UI)": "ux-ui-design.jpg"
        
        
    }
    
    return f"""/media/{mapping.get(nom_filiere, "default.jpg")}""" 

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
                image=get_image_name(article["categorie"]),
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
