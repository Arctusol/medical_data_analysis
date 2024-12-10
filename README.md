# 🏥 Analyse des données hospitalières

## 🎯 Vision du projet
Une approche data-driven pour révolutionner la planification hospitalière en France. Notre projet vise à transformer la gestion des capacités hospitalières en passant d'une approche financière à une approche basée sur les besoins réels de la population.

## 🛠️ Technologies utilisées
- 🐍 Python (Data Science)
- 📊 Streamlit (Interface utilisateur)
- 🗄️ DBT & BigQuery (Data Warehouse)
- 📈 Plotly (Visualisations)
- 🤖 LangChain (Assistant virtuel)

## 🎯 Objectifs principaux
- 📊 Analyser l'évolution des besoins hospitaliers (2018-2022)
- 🔮 Prédire les tendances futures (2023-2025)
- 🚨 Identifier les signaux d'alerte précoces
- 🎯 Créer un outil d'aide à la décision pour les ARS


## 📈 Structure de l'Application

### 🏠 Page d'Accueil
- Vue d'ensemble du projet
- Points clés et indicateurs principaux

### 🌍 Vue générale France
- 📊 Vue globale des indicateurs nationaux
- 🗺️ Carte de France interactive
  - Visualisation géographique des données
  - Analyse régionale comparative

### 🏥 Analyses par Service Médical
- 👨‍⚕️ Chirurgie
- ⚕️ Médecine
- 👶 Obstétrique
- 🧠 Psychiatrie
- ♿ SSR (Soins de Suite et Réadaptation)
- 🏥 ESND

Chaque service propose :
- Évolution temporelle
- Distribution géographique
- Analyse démographique
- Durées moyennes de séjour

### 📊 Modèles Prédictifs
- 📈 Prévisions des tendances
- 🎯 Identification des zones de tension
- 🔄 Analyse des patterns saisonniers
- 🚨 Système d'alerte précoce

### 🤖 Assistant Virtuel
- 💬 Interface conversationnelle
- 🔍 Analyse SQL en langage naturel
- 📊 Génération de visualisations
- 📝 Rapports personnalisés


## 🔧 Installation et Déploiement

### 🚀 Live Demo
Accédez à la version en ligne de l'application :
[https://medicalanalysis.azurewebsites.net/](https://medicalanalysis.azurewebsites.net/)

### 💻 Installation Locale

1. Cloner le repository
```bash
git clone [URL_du_repo]
cd medical_data_analysis
```

2. Créer et activer un environnement virtuel
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/MacOS
python3 -m venv .venv
source .venv/bin/activate
```

3. Installer les dépendances
```bash
pip install -r requirements.txt
```

4. Configuration des variables d'environnement
```bash
# Créer un fichier .env à la racine du projet
touch .env  # ou créer manuellement sous Windows

# Ajouter les variables nécessaires dans .env
AZURE_CONNECTION_STRING=votre_connection_string
OPENAI_API_KEY=votre_api_key
```

5. Lancer l'application
```bash
streamlit run app.py
```

L'application sera accessible à l'adresse : [http://localhost:8501](http://localhost:8501)

### ☁️ Déploiement sur Azure

L'application est déployée sur Azure Web Apps.

## 📊 Sources de Données
- 🏥 DREES (Direction de la Recherche, des Études, de l'Évaluation et des Statistiques)
- 📊 Données hospitalières publiques

## 🎯 Impact attendu

### Pour les ARS
- 📈 Meilleure anticipation des besoins
- 🎯 Allocation optimisée des ressources
- 🚨 Détection précoce des tensions

### Pour les hôpitaux
- 🏥 Planification optimisée des capacités
- 👥 Meilleure prise en charge des patients
- 💰 Optimisation des ressources

### Pour les patients
- ⚡ Réduction des temps d'attente
- 🎯 Soins mieux adaptés aux besoins
- 📈 Amélioration de la qualité des soins

## 🔜 Développements futurs
- 🤖 Amélioration des modèles de ML
- 🌍 Extension à d'autres régions
- 🔄 Intégration de données en temps réel
- 📱 Application mobile pour les décideurs

## 👥 Équipe & contact
Le Wagon projet 2024

## 📚 Documentation
Pour plus de détails techniques :
- 📝 [Documentation détaillée](documentation.md)
