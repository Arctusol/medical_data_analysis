import unittest
import numpy as np
import pandas as pd
from sklearn.datasets import make_classification, make_regression
from ...classification_service.service_classifier import train_service_classifier
from ...duration_prediction.duration_predictor import train_duration_predictor
from ...recommendation.hospital_recommender import HospitalRecommender
from ..metrics import (
    evaluate_service_classification,
    evaluate_duration_prediction,
    evaluate_recommendations
)

class TestServiceClassifier(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Prépare les données de test pour la classification"""
        # Créer des données synthétiques pour les tests
        X, y = make_classification(
            n_samples=1000,
            n_features=20,
            n_informative=15,
            n_redundant=5,
            n_classes=6,
            random_state=42
        )
        
        # Convertir en DataFrame avec les noms de colonnes appropriés
        feature_names = [
            'pathologie', 'code_pathologie', 'nom_pathologie',
            *[f'tranche_age_{i}' for i in range(11)],
            'tx_brut_tt_age_pour_mille',
            'tx_standard_tt_age_pour_mille',
            *[f'feature_{i}' for i in range(4)]
        ]
        cls.data = pd.DataFrame(X, columns=feature_names)
        cls.data['classification'] = y
    
    def test_model_training(self):
        """Teste l'entraînement du modèle de classification"""
        model, encoders = train_service_classifier(self.data)
        self.assertIsNotNone(model)
        self.assertIsNotNone(encoders)
    
    def test_prediction_shape(self):
        """Teste la forme des prédictions"""
        model, encoders = train_service_classifier(self.data)
        predictions = model.predict(self.data)
        self.assertEqual(len(predictions), len(self.data))
    
    def test_evaluation_metrics(self):
        """Teste les métriques d'évaluation"""
        model, encoders = train_service_classifier(self.data)
        predictions = model.predict(self.data)
        metrics = evaluate_service_classification(
            self.data['classification'],
            predictions
        )
        
        required_metrics = ['accuracy', 'macro_precision', 'macro_recall', 'macro_f1']
        for metric in required_metrics:
            self.assertIn(metric, metrics)
            self.assertGreaterEqual(metrics[metric], 0)
            self.assertLessEqual(metrics[metric], 1)

class TestDurationPredictor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Prépare les données de test pour la régression"""
        # Créer des données synthétiques pour les tests
        X, y = make_regression(
            n_samples=1000,
            n_features=20,
            noise=0.1,
            random_state=42
        )
        
        # Convertir en DataFrame avec les noms de colonnes appropriés
        feature_names = [
            'pathologie', 'code_pathologie', 'nom_pathologie',
            'classification', 'sexe',
            *[f'tranche_age_{i}' for i in range(11)],
            *[f'feature_{i}' for i in range(4)]
        ]
        cls.data = pd.DataFrame(X, columns=feature_names)
        cls.data['AVG_duree_hospi'] = np.abs(y)  # Durées toujours positives
    
    def test_model_training(self):
        """Teste l'entraînement du modèle de régression"""
        model, encoders = train_duration_predictor(self.data)
        self.assertIsNotNone(model)
        self.assertIsNotNone(encoders)
    
    def test_prediction_shape(self):
        """Teste la forme des prédictions"""
        model, encoders = train_duration_predictor(self.data)
        predictions = model.predict(self.data)
        self.assertEqual(len(predictions), len(self.data))
    
    def test_evaluation_metrics(self):
        """Teste les métriques d'évaluation"""
        model, encoders = train_duration_predictor(self.data)
        predictions = model.predict(self.data)
        metrics = evaluate_duration_prediction(
            self.data['AVG_duree_hospi'],
            predictions
        )
        
        required_metrics = ['mae', 'rmse', 'r2', 'mape']
        for metric in required_metrics:
            self.assertIn(metric, metrics)
            self.assertGreaterEqual(metrics[metric], 0)

class TestRecommendationSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Prépare les données de test pour le système de recommandation"""
        cls.recommender = HospitalRecommender()
        
        # Créer des données synthétiques pour les hôpitaux
        cls.hospital_data = pd.DataFrame({
            'nom_region': [f'Hospital_{i}' for i in range(10)],
            'classification': ['M', 'C', 'SSR', 'O', 'PSY'] * 2,
            'lit_hospi_complete': np.random.randint(50, 500, 10),
            'hospi_total_24h': np.random.randint(10, 100, 10)
        })
        
        cls.patient_data = {
            'age': 45,
            'sexe': 'H',
            'pathologie': 'example_pathology',
            'region': 'Example Region'
        }
    
    def test_recommendation_structure(self):
        """Teste la structure des recommandations"""
        self.recommender.load_hospital_data(self.hospital_data)
        recommendations = self.recommender.predict(self.patient_data)
        
        self.assertIsInstance(recommendations, list)
        if recommendations:
            required_keys = [
                'hospital_name', 'service', 'score',
                'distance_score', 'capacity_score', 'service_score'
            ]
            for key in required_keys:
                self.assertIn(key, recommendations[0])
    
    def test_recommendation_scoring(self):
        """Teste le scoring des recommandations"""
        self.recommender.load_hospital_data(self.hospital_data)
        recommendations = self.recommender.predict(self.patient_data)
        
        if recommendations:
            # Vérifier que les scores sont triés par ordre décroissant
            scores = [rec['score'] for rec in recommendations]
            self.assertEqual(scores, sorted(scores, reverse=True))
            
            # Vérifier que les scores sont dans l'intervalle [0, 1]
            for rec in recommendations:
                self.assertGreaterEqual(rec['score'], 0)
                self.assertLessEqual(rec['score'], 1)

if __name__ == '__main__':
    unittest.main()
