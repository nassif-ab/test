from sqlalchemy.orm import Session
from models import Post
from crud import create_post
from schemas import PostCreate
from database import SessionLocal

# Obtener una sesión de base de datos
db = SessionLocal()

articles = [
  {
    "titre": "Introduction à l'Intelligence Artificielle",
    "image": "/post.jpg",
    "contenu": "L'intelligence artificielle (IA) transforme de nombreux secteurs, de la santé à la finance. Elle permet aux machines de simuler l'intelligence humaine pour réaliser des tâches telles que la reconnaissance vocale, la traduction automatique et la prise de décision. Cet article présente les bases de l'IA et ses principales applications.",
    "categorie": "Intelligence Artificielle"
  },
  {
    "titre": "Installation d’un environnement de développement Python",
    "image": "/post.jpg",
    "contenu": "Pour commencer le développement en Python, il est essentiel d’installer un environnement adapté. Cela inclut l’installation de Python, d’un éditeur de code comme VS Code, et d’un gestionnaire de paquets tel que pip ou conda. Ce guide vous explique comment configurer votre environnement pas à pas.",
    "categorie": "Développement"
  },
  {
    "titre": "Utilisation de Docker pour les projets Data",
    "image": "/post.jpg",
    "contenu": "Docker est devenu un outil incontournable pour les data engineers et les développeurs. Il permet de créer des environnements reproductibles et portables pour les projets de science des données. Apprenez comment containeriser vos scripts Python et vos notebooks Jupyter pour une meilleure gestion des dépendances.",
    "categorie": "Sciences des données"
  },
  {
    "titre": "Déployer une API avec FastAPI",
    "image": "/post.jpg",
    "contenu": "FastAPI est un framework Python moderne et rapide pour créer des APIs. Grâce à sa compatibilité avec OpenAPI et sa simplicité, il est idéal pour construire des services backend performants. Dans cet article, découvrez comment créer, documenter et déployer une API REST avec FastAPI.",
    "categorie": "Programmation"
  },
  {
    "titre": "Big Data : Introduction à Apache Spark",
    "image": "/post.jpg",
    "contenu": "Apache Spark est un moteur de traitement distribué largement utilisé dans le Big Data. Il permet le traitement de grandes quantités de données en mémoire, rendant les analyses beaucoup plus rapides. Apprenez les bases de Spark, son architecture, et comment exécuter votre premier job Spark.",
    "categorie": "Big Data"
  },
  {
  "titre": "Qu'est-ce que la science des données ?",
  "image": "/data-science-1.jpg",
  "contenu": "La science des données combine la statistique, la programmation et la connaissance métier pour extraire des insights à partir de grandes quantités de données.",
  "categorie": "Sciences des données"
},
{
  "titre": "Les étapes d'un projet Data Science",
  "image": "/data-science-2.jpg",
  "contenu": "Collecte, nettoyage, analyse, modélisation, visualisation… découvrez les grandes étapes pour mener un projet en science des données.",
  "categorie": "Sciences des données"
},
{
  "titre": "Python vs R : Quel langage choisir pour l'analyse de données ?",
  "image": "/data-science-3.jpg",
  "contenu": "Python est polyvalent, R est statistique. Le choix dépend de votre projet et de votre expérience.",
  "categorie": "Sciences des données"
},
{
  "titre": "Top 5 des bibliothèques Python pour l’analyse de données",
  "image": "/data-science-4.jpg",
  "contenu": "Découvrez Pandas, NumPy, Matplotlib, Seaborn et Scikit-learn pour vos analyses et modèles prédictifs.",
  "categorie": "Sciences des données"
},
{
  "titre": "Visualiser ses données avec Power BI",
  "image": "/data-science-5.jpg",
  "contenu": "Power BI est un outil de visualisation puissant pour transformer vos données en tableaux de bord interactifs.",
  "categorie": "Sciences des données"
}
,
{
  "titre": "Apprendre à coder : par où commencer ?",
  "image": "/dev-1.jpg",
  "contenu": "Débuter en programmation peut être déroutant. Voici un guide pour bien choisir votre premier langage et vos outils.",
  "categorie": "Programmation"
},
{
  "titre": "Les différences entre le Frontend et le Backend",
  "image": "/dev-2.jpg",
  "contenu": "Le frontend concerne l’interface utilisateur, tandis que le backend gère la logique et la base de données.",
  "categorie": "Programmation"
},
{
  "titre": "Créer un site web avec HTML, CSS et JavaScript",
  "image": "/dev-3.jpg",
  "contenu": "Un tutoriel simple pour débuter dans le développement web sans frameworks.",
  "categorie": "Programmation"
},
{
  "titre": "Comprendre les APIs REST",
  "image": "/dev-4.jpg",
  "contenu": "Les APIs permettent à différentes applications de communiquer entre elles. Apprenez à les consommer et les créer.",
  "categorie": "Programmation"
},
{
  "titre": "Introduction à Git et GitHub",
  "image": "/dev-5.jpg",
  "contenu": "La gestion de version est essentielle pour tout développeur. Découvrez les bases de Git avec des exemples pratiques.",
  "categorie": "Programmation"
}

,
{
  "titre": "Les branches de l’ingénierie expliquées",
  "image": "/genie-1.jpg",
  "contenu": "Génie civil, électrique, mécanique, informatique… Un panorama des principales spécialités.",
  "categorie": "Génie"
},
{
  "titre": "Logiciels indispensables pour les ingénieurs",
  "image": "/genie-2.jpg",
  "contenu": "AutoCAD, SolidWorks, MATLAB, Ansys… des outils à connaître dans chaque domaine.",
  "categorie": "Génie"
},
{
  "titre": "Les énergies renouvelables en génie électrique",
  "image": "/genie-3.jpg",
  "contenu": "L’ingénieur joue un rôle clé dans la transition énergétique avec le solaire, l’éolien et l’hydraulique.",
  "categorie": "Génie"
},
{
  "titre": "Projets de robotique pour étudiants en mécatronique",
  "image": "/genie-4.jpg",
  "contenu": "Construire un bras robotique ou un robot suiveur de ligne est un bon point de départ.",
  "categorie": "Génie"
},
{
  "titre": "Construire un pont miniature : projet de génie civil",
  "image": "/genie-5.jpg",
  "contenu": "Un projet pratique qui introduit les notions de charge, structure et matériaux.",
  "categorie": "Génie"
}
,
{
  "titre": "L’offre et la demande : fondement de l’économie",
  "image": "/eco-1.jpg",
  "contenu": "Comprendre comment le prix se fixe en fonction des quantités offertes et demandées.",
  "categorie": "Économie"
},
{
  "titre": "Le rôle de la banque centrale",
  "image": "/eco-2.jpg",
  "contenu": "La politique monétaire, les taux d’intérêt et l’inflation expliqués simplement.",
  "categorie": "Économie"
},
{
  "titre": "Différence entre microéconomie et macroéconomie",
  "image": "/eco-3.jpg",
  "contenu": "Deux approches complémentaires pour analyser les comportements individuels et globaux.",
  "categorie": "Économie"
},
{
  "titre": "Qu’est-ce que le PIB et comment est-il calculé ?",
  "image": "/eco-4.jpg",
  "contenu": "Le Produit Intérieur Brut est un indicateur clé de la santé économique d’un pays.",
  "categorie": "Économie"
},
{
  "titre": "Initiation à la gestion financière pour étudiants",
  "image": "/eco-5.jpg",
  "contenu": "Apprendre à faire un budget, gérer ses dépenses et comprendre les bases de la finance personnelle.",
  "categorie": "Économie"
}
,
{
  "titre": "Les types d’intelligence artificielle : faible vs forte",
  "image": "/ai-1.jpg",
  "contenu": "Comprendre la différence entre une IA spécialisée dans une tâche précise et une IA générale capable d’imiter l’intelligence humaine.",
  "categorie": "Intelligence Artificielle"
},
{
  "titre": "Les réseaux de neurones expliqués simplement",
  "image": "/ai-2.jpg",
  "contenu": "Découvrez comment les réseaux de neurones artificiels imitent le fonctionnement du cerveau pour apprendre à partir de données.",
  "categorie": "Intelligence Artificielle"
},
{
  "titre": "Applications de l’IA dans la santé",
  "image": "/ai-3.jpg",
  "contenu": "Du diagnostic automatisé à la découverte de médicaments, l’IA révolutionne la médecine.",
  "categorie": "Intelligence Artificielle"
},
{
  "titre": "Qu’est-ce que le Machine Learning ?",
  "image": "/ai-4.jpg",
  "contenu": "Le machine learning permet aux machines d’apprendre à partir des données sans être explicitement programmées.",
  "categorie": "Intelligence Artificielle"
},
{
  "titre": "Les dangers de l’IA : biais, éthique et emploi",
  "image": "/ai-5.jpg",
  "contenu": "Quels sont les risques liés à l’IA ? Un article qui explore les débats actuels sur son impact social et éthique.",
  "categorie": "Intelligence Artificielle"
}
,
{
  "titre": "Qu’est-ce que le Bitcoin ?",
  "image": "/crypto-1.jpg",
  "contenu": "Bitcoin est la première crypto-monnaie décentralisée basée sur la technologie blockchain. Apprenez son fonctionnement.",
  "categorie": "Crypto & Blockchain"
},
{
  "titre": "Blockchain : une révolution technologique",
  "image": "/crypto-2.jpg",
  "contenu": "La blockchain permet des transactions sécurisées et transparentes sans intermédiaire. Voici comment elle fonctionne.",
  "categorie": "Crypto & Blockchain"
},
{
  "titre": "Les différences entre Bitcoin, Ethereum et d’autres cryptos",
  "image": "/crypto-3.jpg",
  "contenu": "Un guide pour comprendre les usages et les particularités des principales crypto-monnaies.",
  "categorie": "Crypto & Blockchain"
},
{
  "titre": "Mining : comment sont créés les bitcoins ?",
  "image": "/crypto-4.jpg",
  "contenu": "Le minage est le processus qui valide les transactions et crée de nouveaux bitcoins. Découvrez ce qu’il implique.",
  "categorie": "Crypto & Blockchain"
},
{
  "titre": "NFT : l’art numérique à l’ère de la blockchain",
  "image": "/crypto-5.jpg",
  "contenu": "Les jetons non fongibles (NFT) permettent de certifier des œuvres numériques. Ce phénomène change le marché de l’art.",
  "categorie": "Crypto & Blockchain"
}

]

def seed_posts(user_id=1):
    print(f"Agregando {len(articles)} artículos a la base de datos...")
    for article in articles:
        # Convertir los datos del artículo al formato esperado por el backend
        post_data = {
            "title": article["titre"],
            "content": article["contenu"],
            "image": article["image"],
            "categorie": article["categorie"]
        }
        # Crear el post asociado al usuario con ID user_id
        post = create_post(db, PostCreate(**post_data), user_id)
        print(f"Artículo creado: {post.title}")
    
    print("Datos de ejemplo agregados con éxito.")
    db.close()

# Ejecutar la función si este script se ejecuta directamente
if __name__ == "__main__":
    seed_posts()