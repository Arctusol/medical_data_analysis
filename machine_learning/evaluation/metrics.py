import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_absolute_error, mean_squared_error, r2_score,
    confusion_matrix
)
from typing import Dict, List, Tuple
import pandas as pd

def evaluate_service_classification(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: List[str] = None
) -> Dict[str, float]:
    """
    Évalue les performances du modèle de classification des services
    
    Args:
        y_true: Valeurs réelles
        y_pred: Prédictions du modèle
        labels: Liste des labels de services
        
    Returns:
        Dictionnaire contenant les différentes métriques
    """
    metrics = {
        'accuracy': accuracy_score(y_true, y_pred),
        'macro_precision': precision_score(y_true, y_pred, average='macro'),
        'macro_recall': recall_score(y_true, y_pred, average='macro'),
        'macro_f1': f1_score(y_true, y_pred, average='macro')
    }
    
    # Calculer les métriques par service si les labels sont fournis
    if labels:
        conf_matrix = confusion_matrix(y_true, y_pred)
        per_class_metrics = {}
        
        for i, label in enumerate(labels):
            true_pos = conf_matrix[i, i]
            false_pos = conf_matrix[:, i].sum() - true_pos
            false_neg = conf_matrix[i, :].sum() - true_pos
            
            precision = true_pos / (true_pos + false_pos) if (true_pos + false_pos) > 0 else 0
            recall = true_pos / (true_pos + false_neg) if (true_pos + false_neg) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            per_class_metrics[f'{label}_precision'] = precision
            per_class_metrics[f'{label}_recall'] = recall
            per_class_metrics[f'{label}_f1'] = f1
        
        metrics.update(per_class_metrics)
    
    return metrics

def evaluate_duration_prediction(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> Dict[str, float]:
    """
    Évalue les performances du modèle de prédiction de durée
    
    Args:
        y_true: Durées réelles
        y_pred: Durées prédites
        
    Returns:
        Dictionnaire contenant les différentes métriques
    """
    metrics = {
        'mae': mean_absolute_error(y_true, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
        'r2': r2_score(y_true, y_pred),
        'mape': np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    }
    
    # Calculer les erreurs par tranche de durée
    duration_ranges = [(0, 3), (4, 7), (8, 14), (15, 30), (30, float('inf'))]
    for start, end in duration_ranges:
        mask = (y_true >= start) & (y_true <= end)
        if mask.any():
            range_mae = mean_absolute_error(y_true[mask], y_pred[mask])
            metrics[f'mae_{start}_{end}_days'] = range_mae
    
    return metrics

def evaluate_recommendations(
    recommendations: List[Dict],
    ground_truth: Dict,
    top_n: int = 5
) -> Dict[str, float]:
    """
    Évalue la qualité des recommandations
    
    Args:
        recommendations: Liste des recommandations générées
        ground_truth: Données réelles sur les hôpitaux appropriés
        top_n: Nombre de recommandations à considérer
        
    Returns:
        Dictionnaire contenant les métriques d'évaluation
    """
    metrics = {}
    
    # Précision@K
    correct_recommendations = sum(
        1 for rec in recommendations[:top_n]
        if rec['hospital_name'] in ground_truth['appropriate_hospitals']
    )
    metrics['precision_at_k'] = correct_recommendations / min(top_n, len(recommendations))
    
    # Score moyen de pertinence
    if 'relevance_scores' in ground_truth:
        avg_relevance = np.mean([
            ground_truth['relevance_scores'].get(rec['hospital_name'], 0)
            for rec in recommendations[:top_n]
        ])
        metrics['avg_relevance'] = avg_relevance
    
    # Distance moyenne des recommandations
    if all('distance_score' in rec for rec in recommendations[:top_n]):
        avg_distance_score = np.mean([
            rec['distance_score'] for rec in recommendations[:top_n]
        ])
        metrics['avg_distance_score'] = avg_distance_score
    
    # Diversité des services recommandés
    unique_services = len(set(
        rec['service'] for rec in recommendations[:top_n]
    ))
    metrics['service_diversity'] = unique_services / top_n
    
    return metrics

def evaluate_temporal_stability(
    model,
    temporal_test_sets: List[Tuple[pd.DataFrame, pd.DataFrame]],
    metric_func: callable
) -> Dict[str, List[float]]:
    """
    Évalue la stabilité temporelle des prédictions
    
    Args:
        model: Modèle à évaluer
        temporal_test_sets: Liste de tuples (X, y) pour différentes périodes
        metric_func: Fonction de métrique à utiliser
        
    Returns:
        Dictionnaire contenant l'évolution des métriques dans le temps
    """
    temporal_metrics = {
        'metric_values': [],
        'relative_changes': []
    }
    
    previous_metrics = None
    for X_test, y_test in temporal_test_sets:
        # Calculer les métriques pour cette période
        y_pred = model.predict(X_test)
        current_metrics = metric_func(y_test, y_pred)
        
        temporal_metrics['metric_values'].append(current_metrics)
        
        # Calculer le changement relatif si ce n'est pas la première période
        if previous_metrics is not None:
            relative_change = {
                k: (v - previous_metrics[k]) / previous_metrics[k]
                for k, v in current_metrics.items()
            }
            temporal_metrics['relative_changes'].append(relative_change)
        
        previous_metrics = current_metrics
    
    return temporal_metrics
