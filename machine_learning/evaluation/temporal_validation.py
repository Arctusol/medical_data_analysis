import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Any
from sklearn.model_selection import TimeSeriesSplit
from .metrics import (
    evaluate_service_classification,
    evaluate_duration_prediction,
    evaluate_recommendations
)

class TemporalValidator:
    """
    Classe pour effectuer la validation temporelle des modèles
    """
    
    def __init__(
        self,
        n_splits: int = 3,
        test_size: int = 1,
        gap: int = 0
    ):
        """
        Initialise le validateur temporel
        
        Args:
            n_splits: Nombre de splits temporels
            test_size: Taille de l'ensemble de test en années
            gap: Écart entre train et test en années
        """
        self.n_splits = n_splits
        self.test_size = test_size
        self.gap = gap
        self.tscv = TimeSeriesSplit(
            n_splits=n_splits,
            test_size=test_size,
            gap=gap
        )
    
    def prepare_temporal_splits(
        self,
        data: pd.DataFrame,
        date_column: str = 'annee'
    ) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
        """
        Prépare les splits temporels des données
        
        Args:
            data: DataFrame contenant les données
            date_column: Nom de la colonne contenant les dates
            
        Returns:
            Liste de tuples (train, test) pour chaque split
        """
        splits = []
        sorted_data = data.sort_values(date_column)
        
        for train_idx, test_idx in self.tscv.split(sorted_data):
            train_data = sorted_data.iloc[train_idx]
            test_data = sorted_data.iloc[test_idx]
            splits.append((train_data, test_data))
        
        return splits
    
    def validate_service_classifier(
        self,
        model_trainer: callable,
        data: pd.DataFrame,
        target_col: str = 'classification'
    ) -> Dict[str, List[Dict[str, float]]]:
        """
        Valide le modèle de classification des services
        
        Args:
            model_trainer: Fonction d'entraînement du modèle
            data: DataFrame contenant les données
            target_col: Nom de la colonne cible
            
        Returns:
            Dictionnaire contenant les métriques pour chaque split
        """
        splits = self.prepare_temporal_splits(data)
        results = []
        
        for train_data, test_data in splits:
            # Entraîner le modèle
            model, encoders = model_trainer(train_data)
            
            # Faire des prédictions
            X_test = test_data.drop(columns=[target_col])
            y_test = test_data[target_col]
            y_pred = model.predict(X_test)
            
            # Évaluer
            metrics = evaluate_service_classification(y_test, y_pred)
            results.append(metrics)
        
        return {
            'split_metrics': results,
            'avg_metrics': {
                k: np.mean([r[k] for r in results])
                for k in results[0].keys()
            }
        }
    
    def validate_duration_predictor(
        self,
        model_trainer: callable,
        data: pd.DataFrame,
        target_col: str = 'AVG_duree_hospi'
    ) -> Dict[str, List[Dict[str, float]]]:
        """
        Valide le modèle de prédiction de durée
        
        Args:
            model_trainer: Fonction d'entraînement du modèle
            data: DataFrame contenant les données
            target_col: Nom de la colonne cible
            
        Returns:
            Dictionnaire contenant les métriques pour chaque split
        """
        splits = self.prepare_temporal_splits(data)
        results = []
        
        for train_data, test_data in splits:
            # Entraîner le modèle
            model, encoders = model_trainer(train_data)
            
            # Faire des prédictions
            X_test = test_data.drop(columns=[target_col])
            y_test = test_data[target_col]
            y_pred = model.predict(X_test)
            
            # Évaluer
            metrics = evaluate_duration_prediction(y_test, y_pred)
            results.append(metrics)
        
        return {
            'split_metrics': results,
            'avg_metrics': {
                k: np.mean([r[k] for r in results])
                for k in results[0].keys()
            }
        }
    
    def validate_recommendation_system(
        self,
        recommender: Any,
        data: pd.DataFrame,
        test_cases: List[Dict]
    ) -> Dict[str, List[Dict[str, float]]]:
        """
        Valide le système de recommandation
        
        Args:
            recommender: Instance du système de recommandation
            data: DataFrame contenant les données des hôpitaux
            test_cases: Liste de cas de test avec vérité terrain
            
        Returns:
            Dictionnaire contenant les métriques pour chaque cas de test
        """
        splits = self.prepare_temporal_splits(data)
        results = []
        
        for train_data, _ in splits:
            # Mettre à jour les données d'hôpitaux
            recommender.load_hospital_data(train_data)
            
            # Tester chaque cas
            split_results = []
            for test_case in test_cases:
                recommendations = recommender.predict(test_case['patient_data'])
                metrics = evaluate_recommendations(
                    recommendations,
                    test_case['ground_truth']
                )
                split_results.append(metrics)
            
            results.append(split_results)
        
        # Calculer les moyennes
        avg_metrics = {}
        for metric in results[0][0].keys():
            values = [
                result[metric]
                for split in results
                for result in split
            ]
            avg_metrics[metric] = np.mean(values)
        
        return {
            'split_metrics': results,
            'avg_metrics': avg_metrics
        }
    
    def analyze_temporal_trends(
        self,
        validation_results: Dict[str, List[Dict[str, float]]]
    ) -> Dict[str, Any]:
        """
        Analyse les tendances temporelles dans les résultats
        
        Args:
            validation_results: Résultats de la validation
            
        Returns:
            Dictionnaire contenant l'analyse des tendances
        """
        trends = {}
        
        # Calculer les tendances pour chaque métrique
        split_metrics = validation_results['split_metrics']
        for metric in split_metrics[0].keys():
            values = [split[metric] for split in split_metrics]
            
            # Calculer la pente de la tendance
            x = np.arange(len(values))
            slope = np.polyfit(x, values, 1)[0]
            
            # Calculer la stabilité (écart-type)
            stability = np.std(values)
            
            trends[metric] = {
                'slope': slope,
                'stability': stability,
                'values': values
            }
        
        return trends
