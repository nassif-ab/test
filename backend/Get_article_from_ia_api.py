from google import genai
import json
import os
import time

def setup_output_directory(directory="generated_articles"):
    """Create output directory if it doesn't exist."""
    os.makedirs(directory, exist_ok=True)
    return directory

def generate_article_json(client, topic, index, output_dir, catg):
    """Generate an article in JSON format directly from Gemini."""
    try:
        # Create a prompt that asks Gemini to return a properly formatted JSON
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"""
            Je voudrais écrire un article sur le sujet suivant : {topic}
            
            I need you to return ONLY a valid JSON object with the following structure, and nothing else:
            {{
              "titre": "{topic}",
              "image": "/post.jpg",
              "contenu": "[Ici, vous devriez mettre un article détaillé format markdown en Français sur :{topic}]",
              "categorie": "[Choisissez une seule catégorie appropriée à partir de cette liste : {', '.join(catg)}]"
            }}

            Make sure the JSON is valid and properly formatted. Do not include any markdown code blocks or explanations.
            Just return the raw JSON object.
            """,
        )
        
        # Extract the JSON content
        content = response.text.strip()
        
        # Remove any potential markdown code blocks that Gemini might add
        if content.startswith("```json"):
            content = content.replace("```json", "", 1)
        if content.endswith("```"):
            content = content.rsplit("```", 1)[0]
            
        content = content.strip()
        
        # Try to parse the content as JSON to verify it's valid
        try:
            json_obj = json.loads(content)
            
            # Save as both JSON and TXT files
            json_file_path = os.path.join(output_dir, f"{index}_file.json")
                            
            # Also save as proper JSON file
            with open(json_file_path, "w", encoding="utf-8") as f:
                json.dump(json_obj, f, ensure_ascii=False, indent=2)
                
            print(f"✅ Successfully generated article about '{topic}'")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Gemini returned invalid JSON for '{topic}': {str(e)}")
            print(f"Raw content: {content}")
            
            # Save the raw text anyway for inspection
            with open(os.path.join(output_dir, f"{index}_file_error.txt"), "w", encoding="utf-8") as f:
                f.write(content)
                
            return False
            
    except Exception as e:
        print(f"❌ Error generating article for '{topic}': {str(e)}")
        return False

def main():
    # API configuration
    key_api = "AIzaSyDrtnucWlNKCAeZmtsSBRVnX4uQDkxpAWE"
    client = genai.Client(api_key=key_api)
    
    # Setup output directory
    output_dir = setup_output_directory()
    
    # Liste complète des catégories incluant les nouvelles catégories
    catg = [
        # Catégories originales
        "Génie Informatique",
        "Génie Électrique",
        "Génie Industriel",
        "Génie Mécatronique",
        "Réseaux et Systèmes de Télécommunications",
        "Efficacité Énergétique et Bâtiment Intelligent",
        "Génie Civil",
        "Sécurité des Systèmes d'Information",
        "Intelligence Artificielle et IoT pour l'Industrie 4.0",
        "Management de la Supply Chain",
        "Génie Mécanique et Aéronautique",
        "Génie Électrique et Énergies Renouvelables",
        "Licence en Génie Industriel",
        "Big Data et Analytics",
        "Développement Logiciel",
        "DevOps et CI/CD",
        
        # Nouvelles catégories
        "Blockchain et Technologies Distribuées",
        "Cybersécurité Offensive et Défensive",
        "Systèmes Embarqués et IoT",
        "Cloud Computing et Virtualisation",
        "Réalité Virtuelle et Augmentée",
        "Intelligence Artificielle et Data Science",
        "Robotique Avancée",
        "Biotechnologie et Ingénierie Biomédicale",
        "Gestion de Projets Technologiques",
        "Design de l'Expérience Utilisateur (UX/UI)"
    ]

    # 10 sujets pour chaque catégorie (26 catégories × 10 sujets = 260 sujets au total)
    topics = [
        # Génie Informatique (10 sujets)
        "Développement d'une application mobile de gestion de stock pour les PME",
        "Conception d'une architecture microservices pour une plateforme e-commerce",
        "Implémentation d'une solution DevSecOps pour un projet web",
        "Optimisation de la performance d'une application web à forte charge",
        "Création d'un système de gestion de contenu (CMS) personnalisé",
        "Développement d'une plateforme de streaming vidéo en temps réel",
        "Implémentation d'un système de cache distribué pour applications web",
        "Conception d'une API REST sécurisée avec authentification JWT",
        "Développement d'un moteur de recherche personnalisé avec Elasticsearch",
        "Création d'un système de notification push multi-plateforme",

        # Génie Électrique (10 sujets)
        "Conception d'un système de gestion intelligente d'un panneau solaire",
        "Étude et réalisation d'un chargeur rapide pour véhicules électriques",
        "Commande d'un moteur brushless à l'aide d'un microcontrôleur ESP32",
        "Intégration de systèmes embarqués pour la surveillance énergétique",
        "Simulation et analyse d'un réseau électrique intelligent (smart grid)",
        "Conception d'un onduleur pour système photovoltaïque résidentiel",
        "Développement d'un système de protection différentielle pour transformateur",
        "Étude d'un système de compensation d'énergie réactive automatique",
        "Conception d'un variateur de vitesse pour moteur asynchrone",
        "Implémentation d'un système de mesure de qualité d'énergie électrique",

        # Génie Industriel (10 sujets)
        "Optimisation des flux logistiques dans un entrepôt à l'aide de la simulation",
        "Mise en place d'un système Kanban dans une entreprise de fabrication",
        "Application de la méthode Lean Six Sigma pour améliorer un processus industriel",
        "Conception d'un tableau de bord pour le suivi de la performance industrielle",
        "Automatisation de la gestion des stocks avec RFID et IoT",
        "Étude ergonomique d'un poste de travail en chaîne de montage",
        "Optimisation de la planification de production avec algorithmes génétiques",
        "Mise en place d'un système de maintenance prédictive en industrie",
        "Analyse de la chaîne de valeur d'un processus de fabrication",
        "Conception d'un système de traçabilité produit intégré",

        # Génie Mécatronique (10 sujets)
        "Conception et programmation d'un robot suiveur de ligne autonome",
        "Développement d'un bras robotique piloté par vision artificielle",
        "Système de surveillance intelligente pour véhicule (ADAS simplifié)",
        "Contrôle d'un drone autonome via des capteurs embarqués",
        "Simulation d'un système mécatronique pour la fabrication intelligente",
        "Développement d'un système de contrôle de position par servo-moteur",
        "Conception d'un robot mobile à navigation autonome indoor",
        "Implémentation d'un système de régulation de température PID avancé",
        "Développement d'une main robotique avec retour de force",
        "Création d'un système de tri automatique par vision et mécatronique",

        # Réseaux et Systèmes de Télécommunications (10 sujets)
        "Déploiement d'un réseau LTE local avec Open5GS",
        "Mise en œuvre d'un système de VoIP sécurisé avec Asterisk",
        "Étude comparative de protocoles de routage dans un réseau MANET",
        "Sécurisation des communications dans un réseau IoT",
        "Détection d'intrusions réseau à l'aide d'un IDS basé sur le Deep Learning",
        "Optimisation de la QoS dans un réseau d'entreprise multi-services",
        "Conception d'un réseau sans fil maillé pour zones rurales",
        "Implémentation d'un système de communication par satellite",
        "Développement d'une solution SD-WAN pour entreprise distribuée",
        "Analyse de performance d'un réseau 5G en environnement urbain",

        # Efficacité Énergétique et Bâtiment Intelligent (10 sujets)
        "Conception d'un système domotique à faible coût contrôlé par smartphone",
        "Analyse thermique et énergétique d'un bâtiment avec logiciel TRNSYS",
        "Optimisation de la consommation d'énergie d'un bâtiment intelligent avec IoT",
        "Simulation d'un système de ventilation naturel et son impact énergétique",
        "Intégration de panneaux photovoltaïques dans un bâtiment autonome",
        "Développement d'un système de gestion énergétique pour smart building",
        "Conception d'un système de chauffage intelligent adaptatif",
        "Étude d'optimisation de l'éclairage LED avec détection de présence",
        "Implémentation d'un système de monitoring énergétique temps réel",
        "Développement d'une solution de stockage d'énergie pour bâtiment vert",

        # Génie Civil (10 sujets)
        "Étude et dimensionnement d'un pont en béton armé",
        "Optimisation des matériaux de construction pour une durabilité accrue",
        "Conception d'un système de drainage urbain pour zones inondables",
        "Analyse de la résistance sismique d'une structure en béton armé",
        "Simulation de flux de chantier avec MS Project ou Primavera",
        "Étude géotechnique pour fondations d'un bâtiment de grande hauteur",
        "Conception d'une chaussée routière optimisée pour trafic lourd",
        "Analyse de stabilité d'un barrage en terre par éléments finis",
        "Développement d'un système de monitoring structural pour pont suspendu",
        "Étude d'impact environnemental d'un projet d'infrastructure urbaine",

        # Sécurité des Systèmes d'Information (10 sujets)
        "Détection d'attaques par ransomware via analyse comportementale",
        "Mise en œuvre d'un SIEM open-source pour la supervision de sécurité",
        "Étude de la sécurité des API RESTful dans les systèmes d'entreprise",
        "Analyse des risques liés à la cybersécurité dans les systèmes industriels (SCADA)",
        "Application des normes ISO 27001 dans un système d'information hospitalier",
        "Développement d'un système de chiffrement end-to-end pour messagerie",
        "Implémentation d'un système d'authentification multi-facteurs (MFA)",
        "Audit de sécurité d'une infrastructure réseau d'entreprise",
        "Conception d'un plan de continuité d'activité et de reprise après sinistre",
        "Développement d'un système de détection de fraude bancaire en temps réel",

        # Intelligence Artificielle et IoT pour l'Industrie 4.0 (10 sujets)
        "Système de maintenance prédictive basé sur l'IA pour une ligne de production",
        "Surveillance environnementale via capteurs IoT et traitement IA",
        "Optimisation énergétique d'un site industriel par Deep Reinforcement Learning",
        "Détection de défauts de fabrication à l'aide de vision par ordinateur",
        "Intégration d'un système IoT intelligent pour la gestion des ressources en usine",
        "Développement d'un jumeau numérique pour processus de fabrication",
        "Implémentation d'un système de planification intelligente par IA",
        "Création d'un réseau de capteurs auto-adaptatifs pour Industry 4.0",
        "Développement d'un système de contrôle qualité automatisé par IA",
        "Conception d'une chaîne de production flexible pilotée par IA",

        # Management de la Supply Chain (10 sujets)
        "Application du Data Analytics dans l'optimisation de la chaîne logistique",
        "Étude d'impact de la digitalisation sur la performance logistique",
        "Conception d'un tableau de bord KPI pour le suivi de la supply chain",
        "Intégration d'un WMS (Warehouse Management System) dans un entrepôt",
        "Simulation d'un réseau logistique résilient face aux crises",
        "Développement d'un système de prévision de la demande par machine learning",
        "Optimisation des tournées de livraison avec algorithmes de routage",
        "Implémentation d'un système de traçabilité blockchain pour supply chain",
        "Conception d'un modèle de collaboration inter-entreprises dans la logistique",
        "Développement d'un système de gestion des risques supply chain",

        # Génie Mécanique et Aéronautique (10 sujets)
        "Étude aérodynamique d'un drone via simulation CFD",
        "Conception d'un mini-compresseur pour système de propulsion",
        "Optimisation d'une structure d'aile d'avion par la méthode des éléments finis",
        "Étude thermique d'un moteur à combustion interne",
        "Réalisation d'un prototype de système de freinage automatique",
        "Simulation de vol d'un UAV avec contrôle de stabilité",
        "Analyse vibratoire d'une turbine par méthodes numériques",
        "Conception d'un système de refroidissement pour moteur d'avion",
        "Étude de fatigue des matériaux pour structure aéronautique",
        "Développement d'un système de navigation inertielle pour drone",

        # Génie Électrique et Énergies Renouvelables (10 sujets)
        "Dimensionnement d'un système photovoltaïque pour maison isolée",
        "Suivi et analyse de la performance d'un champ solaire réel",
        "Étude d'un convertisseur DC-DC pour applications solaires",
        "Conception d'une éolienne domestique intelligente",
        "Monitoring en temps réel de l'énergie produite par capteurs solaires",
        "Développement d'un système de stockage d'énergie par batteries lithium",
        "Conception d'un micro-réseau hybride (solaire-éolien-diesel)",
        "Étude d'optimisation d'un parc éolien offshore",
        "Implémentation d'un système de gestion intelligente de batterie (BMS)",
        "Développement d'une solution de charge bidirectionnelle V2G",

        # Licence en Génie Industriel (10 sujets)
        "Optimisation de l'implantation d'un atelier industriel",
        "Analyse des coûts de non-qualité dans une chaîne de production",
        "Amélioration de la gestion des déchets dans un site industriel",
        "Évaluation de la productivité à l'aide de la méthode OEE",
        "Mise en place d'un système qualité ISO 9001 dans une PME",
        "Étude de temps et mouvements pour amélioration de postes de travail",
        "Conception d'un système de production Just-In-Time (JIT)",
        "Analyse ABC pour optimisation de la gestion des stocks",
        "Implémentation d'une démarche 5S dans un atelier de production",
        "Développement d'un système de suggestion d'amélioration continue",

        # Big Data et Analytics (10 sujets)
        "Implémentation d'un pipeline ETL avec Apache Airflow pour l'analyse de données massives",
        "Conception d'une architecture lambda pour le traitement temps réel et batch de données",
        "Utilisation de Spark pour l'analyse prédictive dans un contexte e-commerce",
        "Mise en place d'un data lake avec technologies Hadoop pour entreprise industrielle",
        "Développement d'un tableau de bord BI avec visualisation de données massives",
        "Création d'un système de recommandation basé sur le machine learning",
        "Implémentation d'un moteur d'analyse de sentiment sur réseaux sociaux",
        "Développement d'une solution de détection d'anomalies en temps réel",
        "Conception d'un système de scoring client avec algorithmes de classification",
        "Création d'un data warehouse pour analyse décisionnelle multi-dimensionnelle",

        # Développement Logiciel (10 sujets)
        "Implémentation d'une PWA (Progressive Web App) pour la gestion de planning",
        "Développement d'un backend RESTful avec Django pour application de services",
        "Architecture clean code et patrons de conception dans une application mobile Flutter",
        "Création d'une application SPA (Single Page Application) avec React et Redux",
        "Développement d'une API GraphQL pour systèmes distribués",
        "Implémentation d'un système de chat en temps réel avec WebSocket",
        "Développement d'une application desktop cross-platform avec Electron",
        "Création d'un système de gestion de versions distribuée Git avancé",
        "Développement d'une application de réalité augmentée mobile",
        "Implémentation d'un framework de testing automatisé complet",

        # DevOps et CI/CD (10 sujets)
        "Mise en place d'un pipeline CI/CD avec GitLab pour déploiement continu en production",
        "Orchestration de conteneurs avec Kubernetes pour une architecture microservices",
        "Infrastructure as Code (IaC) avec Terraform et Ansible pour environnements hybrides",
        "Monitoring et observabilité d'applications cloud-native avec Prometheus et Grafana",
        "Implémentation de méthodes GitOps pour automatisation de déploiements sécurisés",
        "Création d'un environnement de développement containerisé avec Docker Compose",
        "Mise en place d'une stratégie de déploiement blue-green avec Kubernetes",
        "Développement d'un système de rollback automatique en cas d'échec",
        "Implémentation de la sécurité DevSecOps dans le pipeline CI/CD",
        "Création d'un système de notification et alerting pour opérations DevOps",

        # Blockchain et Technologies Distribuées (10 sujets)
        "Développement d'une application de traçabilité sur blockchain Hyperledger Fabric",
        "Implémentation d'un contrat intelligent sur Ethereum pour la certification de documents",
        "Étude comparative des algorithmes de consensus pour blockchains publiques",
        "Conception d'un système de vote électronique basé sur la blockchain",
        "Développement d'une solution DeFi (Finance Décentralisée) avec smart contracts",
        "Création d'un système de micropaiements avec Lightning Network",
        "Implémentation d'une solution d'identité numérique décentralisée",
        "Développement d'un marché NFT personnalisé sur blockchain",
        "Conception d'un système de supply chain transparent avec blockchain",
        "Création d'une crypto-monnaie personnalisée avec mécanisme de staking",

        # Cybersécurité Offensive et Défensive (10 sujets)
        "Analyse forensique d'un système Linux compromis",
        "Développement d'un honeypot intelligent pour collecter des données sur les attaquants",
        "Conception d'un système de détection d'anomalies basé sur l'apprentissage automatique",
        "Audit de sécurité d'une application web avec outils OWASP",
        "Implementation d'un SOC (Security Operations Center) pour PME",
        "Développement d'un outil de pentest automatisé pour infrastructure réseau",
        "Création d'un système de threat hunting proactif",
        "Implémentation d'une solution de sandboxing pour analyse de malware",
        "Développement d'un système de corrélation d'événements de sécurité",
        "Conception d'un framework de réponse automatisée aux incidents",

        # Systèmes Embarqués et IoT (10 sujets)
        "Conception d'un système de surveillance de la qualité de l'air avec capteurs connectés",
        "Développement d'une plateforme IoT pour l'agriculture intelligente",
        "Implémentation d'un réseau LoRaWAN pour applications Smart City",
        "Conception d'un système embarqué low-power pour applications portables",
        "Sécurisation d'un réseau de capteurs IoT avec chiffrement léger",
        "Développement d'un système de monitoring industriel avec protocoles IoT",
        "Création d'un dispositif portable de santé connecté",
        "Implémentation d'un système de géolocalisation indoor précis",
        "Développement d'une solution IoT pour smart parking",
        "Conception d'un système de maintenance prédictive avec capteurs IoT",

        # Cloud Computing et Virtualisation (10 sujets)
        "Migration d'une infrastructure on-premise vers un cloud hybride",
        "Optimisation des coûts d'une infrastructure AWS avec serverless computing",
        "Implémentation d'une solution PaaS avec Kubernetes et Docker",
        "Conception d'une architecture multi-cloud hautement disponible",
        "Virtualisation de postes de travail VDI pour environnement d'entreprise",
        "Développement d'une solution de disaster recovery cloud",
        "Implémentation d'un système de load balancing intelligent",
        "Création d'une plateforme de développement cloud-native",
        "Développement d'une solution de backup automatisé multi-cloud",
        "Conception d'un système de scaling automatique basé sur la charge",

        # Réalité Virtuelle et Augmentée (10 sujets)
        "Développement d'une application de formation en réalité virtuelle pour l'industrie",
        "Conception d'un système de réalité augmentée pour maintenance industrielle",
        "Création d'une expérience immersive pour visites virtuelles",
        "Développement d'une solution de télé-maintenance avec réalité augmentée",
        "Implémentation d'une application médicale utilisant la réalité mixte",
        "Création d'un simulateur de conduite en réalité virtuelle",
        "Développement d'une application éducative interactive en VR",
        "Conception d'un système de visualisation 3D pour architecture",
        "Implémentation d'une solution de collaboration virtuelle pour équipes distantes",
        "Développement d'un jeu éducatif en réalité augmentée",

        # Intelligence Artificielle et Data Science (10 sujets)
        "Développement d'un système de recommandation personnalisé avec apprentissage profond",
        "Implémentation d'un algorithme de NLP pour l'analyse de sentiment sur réseaux sociaux",
        "Conception d'un système de détection de fraude par analyse comportementale",
        "Développement d'un modèle prédictif pour la maintenance industrielle",
        "Création d'un assistant virtuel pour service client avec traitement du langage naturel",
        "Développement d'un système de reconnaissance faciale éthique et sécurisé",
        "Implémentation d'un modèle de deep learning pour diagnostic médical",
        "Création d'un système de trading algorithmique avec IA",
        "Développement d'un modèle de prédiction météorologique avancé",
        "Conception d'un système d'optimisation logistique par reinforcement learning",

        # Robotique Avancée (10 sujets)
        "Développement d'un système de navigation autonome pour robot mobile",
        "Conception d'un bras robotique collaboratif pour environnement industriel",
        "Implémentation d'un algorithme SLAM pour cartographie de terrain inconnu",
        "Développement d'un système de manipulation d'objets par vision artificielle",
        "Création d'un essaim de robots coordonnés pour tâches complexes",
        "Développement d'un robot humanoïde pour assistance aux personnes âgées",
        "Conception d'un robot explorateur pour environnements dangereux",
        "Implémentation d'un système de contrôle adaptatif pour robot marcheur",
        "Développement d'une interface cerveau-machine pour pilotage robotique",
        "Création d'un robot chirurgical de précision télé-opéré",

        # Biotechnologie et Ingénierie Biomédicale (10 sujets)
        "Conception d'un dispositif de surveillance des signes vitaux connecté",
        "Développement d'un système d'analyse d'images médicales par IA",
        "Implémentation d'un algorithme de traitement de signal pour dispositif d'aide auditive",
        "Conception d'une prothèse intelligente avec capteurs embarqués",
        "Développement d'un système de télémédecine pour zones rurales",
        "Création d'un dispositif de diagnostic rapide portable",
        "Développement d'un système de monitoring de patients en temps réel",
        "Conception d'un dispositif de rééducation motrice assistée",
        "Implémentation d'un système d'analyse génétique automatisé",
        "Développement d'une solution de gestion des données de santé sécurisée",

        # Gestion de Projets Technologiques (10 sujets)
        "Implémentation d'une méthodologie Agile adaptée pour projets multidisciplinaires",
        "Développement d'un tableau de bord pour suivi de projets technologiques complexes",
        "Étude d'impact de la méthodologie DevOps sur la gestion de projets logiciels",
        "Conception d'un système de gestion des connaissances pour équipes techniques",
        "Optimisation des processus de prise de décision dans les projets innovants",
        "Développement d'un système de gestion des ressources multi-projets",
        "Implémentation d'une solution de collaboration virtuelle pour équipes distribuées",
        "Création d'un système d'évaluation des risques projets automatisé",
        "Développement d'une plateforme de gestion de portefeuille de projets",
        "Conception d'un système de reporting automatisé pour parties prenantes",

        # Design de l'Expérience Utilisateur (UX/UI) (10 sujets)
        "Conception d'une interface utilisateur adaptative pour applications industrielles",
        "Développement d'un design system complet pour suite logicielle d'entreprise",
        "Étude et optimisation de l'expérience utilisateur d'une plateforme e-learning",
        "Conception d'interfaces accessibles pour utilisateurs à capacités réduites",
        "Développement d'un prototype d'interface conversationnelle (chatbot) avec UX optimisée",
        "Création d'une application mobile avec design centré utilisateur",
        "Développement d'une interface de réalité virtuelle intuitive",
        "Conception d'un tableau de bord exécutif avec visualisation de données avancée",
        "Développement d'une solution UX pour applications IoT grand public",
        "Création d'une expérience utilisateur gamifiée pour application éducative"
    ]

    # Generate articles for all topics
    success_count = 0
    for index, topic in enumerate(topics):
        print(f"\nGenerating {index+1}/{len(topics)}: {topic}")
        success = generate_article_json(client, topic, index, output_dir, catg)
        if success:
            success_count += 1
            
        # Add a short delay between requests to avoid rate limiting
        if index < len(topics) - 1:
            time.sleep(1)
    
    # Print summary
    print(f"\n✨ Generation complete! Successfully generated {success_count}/{len(topics)} articles.")
    print(f"Files saved in directory: {os.path.abspath(output_dir)}")
    print(f"\n📊 Répartition par catégorie (10 sujets chacune):")
    for i, category in enumerate(catg):
        start_index = i * 10 + 1
        end_index = (i + 1) * 10
        print(f"  {category}: articles {start_index}-{end_index}")

if __name__ == "__main__":
    main()