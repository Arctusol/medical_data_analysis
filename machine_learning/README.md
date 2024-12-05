# Système de Recommandation d'Hôpitaux

Ce dossier contient l'ensemble du système de machine learning pour la recommandation d'hôpitaux basée sur les pathologies et les besoins des patients.

## Structure du Projet

```
machine_learning/
├── classification_service/     # Classification du service médical approprié
├── duration_prediction/        # Prédiction de la durée d'hospitalisation
├── recommendation/            # Système de recommandation d'hôpitaux
├── evaluation/                # Évaluation et validation des modèles
│   ├── metrics.py            # Métriques d'évaluation
│   ├── temporal_validation.py # Validation temporelle
│   ├── tests/                # Tests unitaires
│   └── evaluate_models.ipynb  # Notebook d'évaluation
├── utils/                     # Utilitaires et préparation des données
└── model_development/         # Notebooks de développement
```

## Description des Composants

### 1. Classification des Services (`classification_service/`)
- **service_classifier.py** : Module pour prédire le service médical approprié (M, C, SSR, O, ESND, PSY)
- Utilise PyCaret pour l'entraînement automatisé
- Inclut la gestion des encodeurs pour les variables catégorielles
- Features : pathologie, tranches d'âge, taux standardisés, etc.

### 2. Prédiction de Durée (`duration_prediction/`)
- **duration_predictor.py** : Module pour estimer la durée d'hospitalisation
- Optimisé pour la régression
- Utilise des features spécifiques à la durée de séjour
- Intègre le tuning automatique des hyperparamètres

### 3. Système de Recommandation (`recommendation/`)
- **hospital_recommender.py** : Système principal de recommandation
- Combine les prédictions des différents modèles
- Calcule des scores basés sur :
  - Distance géographique
  - Capacité d'accueil
  - Compatibilité des services
  - Durée estimée du séjour

### 4. Évaluation (`evaluation/`)
- **metrics.py** : Métriques personnalisées pour l'évaluation
  - Métriques de classification des services
  - Métriques de prédiction de durée
  - Métriques de qualité des recommandations
- **temporal_validation.py** : Validation temporelle des modèles
  - Splits temporels des données
  - Analyse des tendances
  - Évaluation de la stabilité
- **tests/** : Tests unitaires pour chaque composant
- **evaluate_models.ipynb** : Notebook d'évaluation complète

### 5. Utilitaires (`utils/`)
- **data_preparation.py** : Préparation et chargement des données
- Gestion de la connexion BigQuery
- Préparation des features pour les modèles
- Séparation train/test par années

## État d'Avancement

### Complété 
1. **Structure de Base**
   - Architecture modulaire
   - Intégration avec MLflow et PyCaret
   - Connexion BigQuery

2. **Modèles de Base**
   - Classification des services
   - Prédiction de durée
   - Système de scoring

3. **Évaluation**
   - Framework de métriques
   - Validation temporelle
   - Tests unitaires
   - Notebook d'évaluation

### En Cours 
1. **Optimisation des Modèles**
   - [ ] Affiner les hyperparamètres
   - [ ] Optimiser les poids du système de scoring
   - [ ] Ajouter des features supplémentaires

2. **Interface et Intégration**
   - [ ] Créer une API REST
   - [ ] Développer une interface utilisateur
   - [ ] Intégrer dans l'application principale

### À Faire 
1. **Documentation et Maintenance**
   - [ ] Compléter la documentation utilisateur
   - [ ] Mettre en place le monitoring
   - [ ] Ajouter des exemples d'utilisation

2. **Améliorations Futures**
   - [ ] Intégrer les avis patients
   - [ ] Ajouter des données en temps réel
   - [ ] Développer un système de feedback

## Utilisation

1. Installation des dépendances :
```bash
pip install -r requirements.txt
```

2. Configuration :
- Configurer les credentials BigQuery
- Initialiser MLflow pour le tracking des expériences

3. Évaluation des modèles :
```python
# Exécuter le notebook d'évaluation
jupyter notebook evaluation/evaluate_models.ipynb
```

4. Utilisation du système :
```python
from recommendation.hospital_recommender import HospitalRecommender

recommender = HospitalRecommender()
recommender.load_models(service_run_id='...', duration_run_id='...')
recommendations = recommender.predict(patient_data)
```

## Dépendances Principales

- PyCaret
- MLflow
- Google Cloud BigQuery
- pandas
- scikit-learn
- geopy
- pytest (pour les tests)
- jupyter (pour les notebooks)

## Contribution

Pour contribuer au projet :
1. Créer une nouvelle branche pour chaque feature
2. Suivre les conventions de code établies
3. Documenter les changements
4. Soumettre une pull request

## Contact

Pour toute question ou suggestion, contacter l'équipe de développement.
