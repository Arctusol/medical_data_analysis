import sys
sys.path.append('../')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from google.cloud import bigquery
import os
import mlflow

from utils.data_preparation import (
    load_data,
    prepare_datasets,
    prepare_train_test_data,
    prepare_features_for_service_classification,
    prepare_features_for_duration_prediction
)
from classification_service.service_classifier import train_service_classifier
from duration_prediction.duration_predictor import train_duration_predictor
from recommendation.hospital_recommender import HospitalRecommender
from evaluation.metrics import (
    evaluate_service_classification,
    evaluate_duration_prediction,
    evaluate_recommendations
)

def main():
    # 1. Charger les données
    print("Chargement des données...")
    data_dict = load_data()
    
    # 2. Préparer les datasets
    print("Préparation des datasets...")
    datasets = prepare_datasets(data_dict['morbidite'], data_dict['capacite'])
    
    # 3. Préparer les features pour la classification des services
    print("Préparation des features pour la classification...")
    features_classification = prepare_features_for_service_classification(
        datasets['dpt'],
        datasets['capacite']
    )
    
    # 4. Préparer les features pour la prédiction de durée
    print("Préparation des features pour la prédiction de durée...")
    features_duration = prepare_features_for_duration_prediction(
        datasets['dpt'],
        datasets['capacite']
    )
    
    # 5. Diviser en train/test
    print("Division en train/test...")
    X_train_class, X_test_class = prepare_train_test_data(features_classification)
    X_train_dur, X_test_dur = prepare_train_test_data(features_duration)
    
    # 6. Entraîner et évaluer le modèle de classification
    print("\nÉvaluation du modèle de classification des services...")
    service_model = train_service_classifier(X_train_class)
    service_metrics = evaluate_service_classification(service_model, X_test_class)
    print("Métriques de classification:")
    print(service_metrics)
    
    # 7. Entraîner et évaluer le modèle de prédiction de durée
    print("\nÉvaluation du modèle de prédiction de durée...")
    duration_model = train_duration_predictor(X_train_dur)
    duration_metrics = evaluate_duration_prediction(duration_model, X_test_dur)
    print("Métriques de prédiction de durée:")
    print(duration_metrics)
    
    # 8. Évaluer le système de recommandation complet
    print("\nÉvaluation du système de recommandation...")
    recommender = HospitalRecommender(service_model, duration_model)
    recommendation_metrics = evaluate_recommendations(
        recommender,
        datasets['dpt'],
        datasets['capacite']
    )
    print("Métriques de recommandation:")
    print(recommendation_metrics)
    
    # 9. Sauvegarder les résultats
    results = {
        'service_classification': service_metrics,
        'duration_prediction': duration_metrics,
        'recommendation': recommendation_metrics
    }
    pd.DataFrame(results).to_csv('evaluation_results.csv')
    print("\nRésultats sauvegardés dans evaluation_results.csv")

if __name__ == "__main__":
    main()
