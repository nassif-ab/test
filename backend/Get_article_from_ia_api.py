from google import genai
import json
import os
import time

def setup_output_directory(directory="generated_articles"):
    """Create output directory if it doesn't exist."""
    os.makedirs(directory, exist_ok=True)
    return directory

def generate_article_json(client, topic, index, output_dir,catg):
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
    
    # List of topics to generate articles about
    catg = [
    "Génie Informatique",
    "Génie Électrique",
    "Génie Industriel",
    "Génie Mécatronique",
    "Réseaux et Systèmes de Télécommunications",
    "Efficacité Énergétique et Bâtiment Intelligent",
    "Génie Civil",
    "Sécurité des Systèmes d’Information",
    "Intelligence Artificielle et IoT pour l’Industrie 4.0",
    "Management de la Supply Chain",
    "Génie Mécanique et Aéronautique",
    "Génie Électrique et Énergies Renouvelables",
    "Licence en Génie Industriel"
]
    topics = [
    # Génie Informatique
    "Développement d’une application mobile de gestion de stock pour les PME",
    "Mise en place d’un système de détection d’intrusion basé sur le Machine Learning",
    "Conception d’une architecture microservices pour une plateforme e-commerce",
    "Implémentation d’une solution DevSecOps pour un projet web",
    "Optimisation de la performance d’une application web à forte charge",

    # Génie Électrique
    "Conception d’un système de gestion intelligente d’un panneau solaire",
    "Étude et réalisation d’un chargeur rapide pour véhicules électriques",
    "Commande d’un moteur brushless à l’aide d’un microcontrôleur ESP32",
    "Intégration de systèmes embarqués pour la surveillance énergétique",
    "Simulation et analyse d’un réseau électrique intelligent (smart grid)",

    # Génie Industriel
    "Optimisation des flux logistiques dans un entrepôt à l’aide de la simulation",
    "Mise en place d’un système Kanban dans une entreprise de fabrication",
    "Application de la méthode Lean Six Sigma pour améliorer un processus industriel",
    "Conception d’un tableau de bord pour le suivi de la performance industrielle",
    "Automatisation de la gestion des stocks avec RFID et IoT",

    # Génie Mécatronique
    "Conception et programmation d’un robot suiveur de ligne autonome",
    "Développement d’un bras robotique piloté par vision artificielle",
    "Système de surveillance intelligente pour véhicule (ADAS simplifié)",
    "Contrôle d’un drone autonome via des capteurs embarqués",
    "Simulation d’un système mécatronique pour la fabrication intelligente",

    # Réseaux et Systèmes de Télécommunications
    "Déploiement d’un réseau LTE local avec Open5GS",
    "Mise en œuvre d’un système de VoIP sécurisé avec Asterisk",
    "Étude comparative de protocoles de routage dans un réseau MANET",
    "Sécurisation des communications dans un réseau IoT",
    "Détection d’intrusions réseau à l’aide d’un IDS basé sur le Deep Learning",

    # Efficacité Énergétique et Bâtiment Intelligent
    "Conception d’un système domotique à faible coût contrôlé par smartphone",
    "Analyse thermique et énergétique d’un bâtiment avec logiciel TRNSYS",
    "Optimisation de la consommation d’énergie d’un bâtiment intelligent avec IoT",
    "Simulation d’un système de ventilation naturel et son impact énergétique",
    "Intégration de panneaux photovoltaïques dans un bâtiment autonome",

    # Génie Civil
    "Étude et dimensionnement d’un pont en béton armé",
    "Optimisation des matériaux de construction pour une durabilité accrue",
    "Conception d’un système de drainage urbain pour zones inondables",
    "Analyse de la résistance sismique d’une structure en béton armé",
    "Simulation de flux de chantier avec MS Project ou Primavera",

    # Masters Spécialisés - Sécurité des Systèmes d’Information
    "Détection d’attaques par ransomware via analyse comportementale",
    "Mise en œuvre d’un SIEM open-source pour la supervision de sécurité",
    "Étude de la sécurité des API RESTful dans les systèmes d’entreprise",
    "Analyse des risques liés à la cybersécurité dans les systèmes industriels (SCADA)",
    "Application des normes ISO 27001 dans un système d'information hospitalier",

    # Master en Intelligence Artificielle et IoT pour l’Industrie 4.0
    "Système de maintenance prédictive basé sur l’IA pour une ligne de production",
    "Surveillance environnementale via capteurs IoT et traitement IA",
    "Optimisation énergétique d’un site industriel par Deep Reinforcement Learning",
    "Détection de défauts de fabrication à l’aide de vision par ordinateur",
    "Intégration d’un système IoT intelligent pour la gestion des ressources en usine",

    # Master en Management de la Supply Chain
    "Application du Data Analytics dans l’optimisation de la chaîne logistique",
    "Étude d’impact de la digitalisation sur la performance logistique",
    "Conception d’un tableau de bord KPI pour le suivi de la supply chain",
    "Intégration d’un WMS (Warehouse Management System) dans un entrepôt",
    "Simulation d’un réseau logistique résilient face aux crises",

    # Licences Professionnelles - Génie Mécanique et Aéronautique
    "Étude aérodynamique d’un drone via simulation CFD",
    "Conception d’un mini-compresseur pour système de propulsion",
    "Optimisation d’une structure d’aile d’avion par la méthode des éléments finis",
    "Étude thermique d’un moteur à combustion interne",
    "Réalisation d’un prototype de système de freinage automatique",

    # Licence en Génie Électrique et Énergies Renouvelables
    "Dimensionnement d’un système photovoltaïque pour maison isolée",
    "Suivi et analyse de la performance d’un champ solaire réel",
    "Étude d’un convertisseur DC-DC pour applications solaires",
    "Conception d’une éolienne domestique intelligente",
    "Monitoring en temps réel de l’énergie produite par capteurs solaires",

    # Licence en Génie Industriel
    "Optimisation de l’implantation d’un atelier industriel",
    "Analyse des coûts de non-qualité dans une chaîne de production",
    "Amélioration de la gestion des déchets dans un site industriel",
    "Évaluation de la productivité à l’aide de la méthode OEE",
    "Mise en place d’un système qualité ISO 9001 dans une PME"
]

    
    # Generate articles for all topics
    success_count = 0
    for index, topic in enumerate(topics):
        print(f"\nGenerating {index+1}/{len(topics)}: {topic}")
        success = generate_article_json(client, topic, index, output_dir,catg)
        if success:
            success_count += 1
            
        # Add a short delay between requests to avoid rate limiting
        if index < len(topics) - 1:
            time.sleep(1)
    
    # Print summary
    print(f"\n✨ Generation complete! Successfully generated {success_count}/{len(topics)} articles.")
    print(f"Files saved in directory: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    main()