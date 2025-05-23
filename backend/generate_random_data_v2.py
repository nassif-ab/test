import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from crud import get_users, get_user_by_username, get_user_by_email, create_user
from schemas import UserCreate
import time

# Générateur de données utilisateur
def generate_user_data(count=300):
    """Génère 300 utilisateurs avec des données réalistes"""
    
    # Listes de prénoms et noms en français et arabe
    prenoms_fr = [
        "Ahmed", "Mohamed", "Fatima", "Aicha", "Omar", "Khadija", "Youssef", "Amina",
        "Hassan", "Nadia", "Karim", "Samira", "Rachid", "Leila", "Mehdi", "Zineb",
        "Abdelkader", "Hafsa", "Said", "Malika", "Bilal", "Souad", "Tarik", "Ghita",
        "Khalid", "Rajae", "Hamza", "Siham", "Amine", "Kenza", "Othmane", "Imane",
        "Abderrahim", "Hanane", "Driss", "Widad", "Mustapha", "Hayat", "Saad", "Chaima",
        "Adil", "Rim", "Jamal", "Asma", "Nordine", "Houda", "Zakaria", "Meryem",
        "Reda", "Salma", "Ismail", "Naima", "Fouad", "Laila", "Hicham", "Sara"
    ]
    
    noms_fr = [
        "Benali", "Alami", "Fassi", "Tazi", "Bennani", "Kadiri", "Lamrani", "Berrada",
        "Cherif", "Idrissi", "Hakim", "Naciri", "Squalli", "Cherkaoui", "Benlahcen",
        "Andaloussi", "Belkadi", "Rami", "Sabir", "Tahiri", "Benkirane", "Rais",
        "Benabdellah", "Amrani", "Belkacem", "Benomar", "Filali", "Benjelloun",
        "Kettani", "Benchekroun", "Ghali", "Mekouar", "Skalli", "Benslimane",
        "Bouchentouf", "Lahlou", "Benali", "Chraibi", "Berrechid", "Boukhris"
    ]
    
    domaines_email = ["gmail.com", "hotmail.com", "yahoo.fr", "outlook.com", "email.com"]
    
    users_data = []
    
    for i in range(count):
        prenom = random.choice(prenoms_fr)
        nom = random.choice(noms_fr)
        
        # Générer un nom d'utilisateur unique
        username_base = f"{prenom.lower()}{nom.lower()}"
        username = f"{username_base}{random.randint(1, 9999)}"
        
        # Générer un email unique
        email = f"{prenom.lower()}.{nom.lower()}{random.randint(1, 999)}@{random.choice(domaines_email)}"
        
        user_data = {
            "username": username,
            "fullName": f"{prenom} {nom}",
            "email": email,
            "password": "123456789",  # Mot de passe par défaut
            "is_admin": False
        }
        
        users_data.append(user_data)
    
    return users_data

def create_or_update_user(db: Session, user_data):
    """Crée ou met à jour un utilisateur"""
    # Vérifier si l'utilisateur existe déjà par username
    existing_user = get_user_by_username(db, user_data["username"])
    if existing_user:
        return existing_user, "existe"
    
    # Vérifier si l'utilisateur existe déjà par email
    existing_user = get_user_by_email(db, user_data["email"])
    if existing_user:
        # Modifier l'email pour éviter les doublons
        user_data["email"] = f"modified_{random.randint(1000, 9999)}_{user_data['email']}"
    
    # Créer le nouvel utilisateur
    try:
        user_create = UserCreate(**user_data)
        new_user = create_user(db, user_create)
        return new_user, "creado"
    except Exception as e:
        print(f"Erreur lors de la création de l'utilisateur {user_data['username']}: {e}")
        return None, "erreur"

def get_categories_from_db(db: Session):
    """Récupère les catégories depuis la base de données"""
    print("Récupération des catégories depuis la base de données...")
    categories = []
    
    # Récupérer toutes les catégories uniques depuis la table des posts
    db_categories = db.query(models.Post.categorie).distinct().all()
    
    # Convertir le résultat en liste simple
    for category in db_categories:
        if category[0]:  # Vérifier que la catégorie n'est pas vide
            categories.append(category[0])
    
    print(f"✅ {len(categories)} catégories trouvées dans la base de données")
    return categories

def get_random_date(start_date, end_date):
    """Génère une date aléatoire entre la date de début et la date de fin"""
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    if days_between_dates <= 0:
        return start_date
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)

def assign_user_interests(db: Session, categories):
    """Assigne trois catégories d'intérêt à chaque utilisateur avec différents niveaux d'interaction"""
    print("Attribution d'intérêts personnalisés aux utilisateurs...")
    
    # Récupérer tous les utilisateurs et les posts par catégorie
    users = db.query(models.User).all()
    
    # Créer un dictionnaire pour stocker les posts par catégorie
    posts_by_category = {}
    for category in categories:
        posts_by_category[category] = db.query(models.Post).filter(models.Post.categorie == category).all()
    
    # Supprimer les catégories qui n'ont pas de posts
    categories_with_posts = [cat for cat in categories if posts_by_category[cat]]
    
    if not categories_with_posts:
        print("Aucune catégorie avec des posts pour assigner des intérêts")
        return []
    
    print(f"📊 {len(users)} utilisateurs trouvés")
    print(f"📊 {len(categories_with_posts)} catégories avec des posts")
    
    return users

def generate_personalized_visits_and_likes(db: Session, categories, start_date=None, end_date=None):
    """Génère des visites et likes personnalisés selon les intérêts de chaque utilisateur"""
    print("Génération d'interactions personnalisées selon les intérêts...")
    
    # Configuration des dates
    if start_date is None:
        start_date = datetime.now() - timedelta(days=180)
    if end_date is None:
        end_date = datetime.now()
    
    # Assigner les intérêts et récupérer les utilisateurs
    users = assign_user_interests(db, categories)
    if not users:
        print("Aucun utilisateur pour générer des interactions")
        return
    
    # Créer un dictionnaire pour stocker les posts par catégorie
    posts_by_category = {}
    for category in categories:
        posts_by_category[category] = db.query(models.Post).filter(models.Post.categorie == category).all()
    
    # Ensemble pour éviter la duplication dans les likes
    existing_likes = set()
    likes = db.query(models.Like).all()
    for like in likes:
        existing_likes.add((like.user_id, like.post_id))
    
    # Générer des interactions pour chaque utilisateur
    visits_created = 0
    likes_created = 0
    
    print(f"🔄 Génération d'interactions pour {len(users)} utilisateurs...")
    
    for idx, user in enumerate(users):
        if idx % 50 == 0:  # Afficher le progrès tous les 50 utilisateurs
            print(f"  Progression: {idx}/{len(users)} utilisateurs traités")
        
        # Déterminer les catégories disponibles avec des posts
        categories_with_available_posts = [cat for cat in categories if posts_by_category[cat]]
        if not categories_with_available_posts:
            continue
        
        # Sélectionner 3 catégories différentes au hasard pour l'utilisateur
        if len(categories_with_available_posts) >= 3:
            selected_categories = random.sample(categories_with_available_posts, 3)
        else:
            selected_categories = categories_with_available_posts.copy()
            while len(selected_categories) < 3 and categories_with_available_posts:
                selected_categories.append(random.choice(categories_with_available_posts))
        
        # Niveau 1: Intérêt élevé (beaucoup de visites et likes)
        if selected_categories:
            high_interest_category = selected_categories[0]
            high_interest_posts = posts_by_category[high_interest_category]
            
            # Créer 15-30 visites pour la catégorie d'intérêt élevé
            if high_interest_posts:
                num_visits = random.randint(15, 30)
                for _ in range(num_visits):
                    post = random.choice(high_interest_posts)
                    visit = models.Visit(
                        post_id=post.id,
                        user_id=user.id,
                        ip_address=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                        visit_date=get_random_date(start_date, end_date)
                    )
                    db.add(visit)
                    visits_created += 1
                
                # Créer 8-15 likes pour la catégorie d'intérêt élevé
                num_likes = random.randint(8, 15)
                like_attempts = 0
                likes_added = 0
                
                while likes_added < num_likes and like_attempts < num_likes * 3:
                    like_attempts += 1
                    post = random.choice(high_interest_posts)
                    
                    # Vérifier si ce like existe déjà
                    if (user.id, post.id) in existing_likes:
                        continue
                    
                    like = models.Like(
                        user_id=user.id,
                        post_id=post.id,
                        created_at=get_random_date(start_date, end_date)
                    )
                    db.add(like)
                    existing_likes.add((user.id, post.id))
                    likes_created += 1
                    likes_added += 1
        
        # Niveau 2: Intérêt moyen (visites fréquentes, peu de likes)
        if len(selected_categories) > 1:
            medium_interest_category = selected_categories[1]
            medium_interest_posts = posts_by_category[medium_interest_category]
            
            # Créer 8-15 visites pour la catégorie d'intérêt moyen
            if medium_interest_posts:
                num_visits = random.randint(8, 15)
                for _ in range(num_visits):
                    post = random.choice(medium_interest_posts)
                    visit = models.Visit(
                        post_id=post.id,
                        user_id=user.id,
                        ip_address=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                        visit_date=get_random_date(start_date, end_date)
                    )
                    db.add(visit)
                    visits_created += 1
                
                # Créer 2-6 likes pour la catégorie d'intérêt moyen
                num_likes = random.randint(2, 6)
                like_attempts = 0
                likes_added = 0
                
                while likes_added < num_likes and like_attempts < num_likes * 3:
                    like_attempts += 1
                    post = random.choice(medium_interest_posts)
                    
                    # Vérifier si ce like existe déjà
                    if (user.id, post.id) in existing_likes:
                        continue
                    
                    like = models.Like(
                        user_id=user.id,
                        post_id=post.id,
                        created_at=get_random_date(start_date, end_date)
                    )
                    db.add(like)
                    existing_likes.add((user.id, post.id))
                    likes_created += 1
                    likes_added += 1
        
        # Niveau 3: Intérêt faible (peu de visites, pas de likes)
        if len(selected_categories) > 2:
            low_interest_category = selected_categories[2]
            low_interest_posts = posts_by_category[low_interest_category]
            
            # Créer 1-5 visites pour la catégorie d'intérêt faible
            if low_interest_posts:
                num_visits = random.randint(1, 5)
                for _ in range(num_visits):
                    post = random.choice(low_interest_posts)
                    visit = models.Visit(
                        post_id=post.id,
                        user_id=user.id,
                        ip_address=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                        visit_date=get_random_date(start_date, end_date)
                    )
                    db.add(visit)
                    visits_created += 1
        
        # Commit périodique pour éviter les problèmes de mémoire
        if idx % 25 == 0:
            db.commit()
    
    # Commit final
    db.commit()
    
    print(f"✅ {visits_created} visites personnalisées créées")
    print(f"✅ {likes_created} likes personnalisés créés")

def create_users_from_generated_data(db: Session, count=300):
    """Crée ou met à jour les utilisateurs à partir des données générées"""
    print(f"Création ou mise à jour de {count} utilisateurs...")
    
    # Générer les données utilisateur
    users_data = generate_user_data(count)
    
    users_created = 0
    users_updated = 0
    users_errors = 0
    
    for i, user_data in enumerate(users_data):
        if i % 50 == 0:  # Afficher le progrès tous les 50 utilisateurs
            print(f"  Progression: {i}/{count} utilisateurs traités")
        
        # Créer ou mettre à jour l'utilisateur
        user, action = create_or_update_user(db, user_data)
        
        if action == "creado":
            users_created += 1
        elif action == "existe":
            users_updated += 1
        else:
            users_errors += 1
    
    print(f"✅ {users_created} utilisateurs créés")
    print(f"✅ {users_updated} utilisateurs existants")
    if users_errors > 0:
        print(f"⚠️ {users_errors} erreurs lors de la création")

def clean_existing_interactions(db: Session):
    """Nettoie les interactions existantes pour créer de nouvelles interactions"""
    print("Nettoyage des interactions existantes...")
    
    # Supprimer les likes et visites existants
    likes_count = db.query(models.Like).count()
    visits_count = db.query(models.Visit).count()
    
    db.query(models.Like).delete()
    db.query(models.Visit).delete()
    db.commit()
    
    print(f"✅ {likes_count} likes supprimés")
    print(f"✅ {visits_count} visites supprimées")

def main():
    """Fonction principale"""
    # Créer une session de base de données
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("🚀 GÉNÉRATION DE DONNÉES PERSONNALISÉES - 300 UTILISATEURS")
        print("=" * 60)
        
        # Définir une plage de dates personnalisée (3 derniers mois par défaut)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)  # 3 mois
        
        # Permettre la personnalisation de la plage de dates depuis la ligne de commande
        import sys
        if len(sys.argv) > 2:
            try:
                # Format attendu: YYYY-MM-DD
                start_date = datetime.strptime(sys.argv[1], "%Y-%m-%d")
                end_date = datetime.strptime(sys.argv[2], "%Y-%m-%d")
                print(f"📅 Utilisation d'une plage de dates personnalisée: {start_date.strftime('%Y-%m-%d')} à {end_date.strftime('%Y-%m-%d')}")
            except ValueError:
                print("⚠️ Format de date incorrect. Utilisation des valeurs par défaut.")
                print("Format correct: python script.py 2025-01-01 2025-05-01")
        else:
            print(f"📅 Plage de dates par défaut: {start_date.strftime('%Y-%m-%d')} à {end_date.strftime('%Y-%m-%d')}")
        
        # Étape 1: Créer ou mettre à jour 300 utilisateurs
        print("\n" + "=" * 50)
        print("📝 ÉTAPE 1: CRÉATION DES UTILISATEURS")
        print("=" * 50)
        create_users_from_generated_data(db, count=300)
        
        # Étape 2: Nettoyer les interactions existantes (optionnel)
        print("\n" + "=" * 50)
        print("🧹 ÉTAPE 2: NETTOYAGE DES INTERACTIONS")
        print("=" * 50)
        response = input("Voulez-vous supprimer les interactions existantes? (o/n): ")
        if response.lower() in ['o', 'oui', 'y', 'yes']:
            clean_existing_interactions(db)
        else:
            print("Conservation des interactions existantes...")
        
        # Étape 3: Récupérer les catégories depuis la base de données
        print("\n" + "=" * 50)
        print("📂 ÉTAPE 3: RÉCUPÉRATION DES CATÉGORIES")
        print("=" * 50)
        categories = get_categories_from_db(db)
        
        if not categories:
            print("❌ Aucune catégorie trouvée dans la base de données!")
            print("Assurez-vous d'avoir des posts avec des catégories dans votre base de données.")
            return
        
        # Étape 4: Générer des interactions personnalisées selon les intérêts
        print("\n" + "=" * 50)
        print("🎯 ÉTAPE 4: GÉNÉRATION DES INTERACTIONS")
        print("=" * 50)
        generate_personalized_visits_and_likes(db, categories, start_date=start_date, end_date=end_date)
        
        # Résumé final
        print("\n" + "=" * 60)
        print("🎉 GÉNÉRATION TERMINÉE AVEC SUCCÈS!")
        print("=" * 60)
        
        # Statistiques finales
        total_users = db.query(models.User).count()
        total_visits = db.query(models.Visit).count()
        total_likes = db.query(models.Like).count()
        total_posts = db.query(models.Post).count()
        
        print(f"📊 STATISTIQUES FINALES:")
        print(f"   👥 Utilisateurs totaux: {total_users}")
        print(f"   📝 Posts totaux: {total_posts}")
        print(f"   👁️ Visites totales: {total_visits}")
        print(f"   ❤️ Likes totaux: {total_likes}")
        print(f"   📂 Catégories: {len(categories)}")
        
        print(f"\n💡 Pour améliorer les recommandations, exécutez le script de formation:")
        print(f"   python scheduled_training.py")
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération des données personnalisées: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Fermer la session
        db.close()
        print("\n🔒 Session de base de données fermée.")

if __name__ == "__main__":
    main()