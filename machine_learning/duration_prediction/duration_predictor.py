from pycaret.regression import *
import mlflow
import pandas as pd
from typing import Optional, Tuple, Dict
from sklearn.preprocessing import LabelEncoder

def prepare_duration_data(data: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """
    Prépare les données pour la prédiction de durée
    
    Args:
        data: DataFrame contenant les données brutes
        
    Returns:
        DataFrame préparé et dictionnaire des encodeurs
    """
    # Sélectionner les colonnes pertinentes
    features = [
        'pathologie', 'code_pathologie', 'nom_pathologie',
        'classification', 'sexe',
        'tranche_age_0_1', 'tranche_age_1_4', 'tranche_age_5_14',
        'tranche_age_15_24', 'tranche_age_25_34', 'tranche_age_35_44',
        'tranche_age_45_54', 'tranche_age_55_64', 'tranche_age_65_74',
        'tranche_age_75_84', 'tranche_age_85_et_plus',
        'tx_brut_tt_age_pour_mille', 'tx_standard_tt_age_pour_mille',
        'AVG_duree_hospi'  # target variable
    ]
    
    df = data[features].copy()
    
    # Créer les encodeurs pour les variables catégorielles
    encoders = {}
    categorical_features = ['pathologie', 'nom_pathologie', 'classification', 'sexe']
    
    for feature in categorical_features:
        encoders[feature] = LabelEncoder()
        df[feature] = encoders[feature].fit_transform(df[feature])
    
    return df, encoders

def train_duration_predictor(
    data: pd.DataFrame,
    target_col: str = 'AVG_duree_hospi',
    fold: int = 5,
    experiment_name: str = 'duration_prediction'
) -> Tuple[object, Dict]:
    """
    Entraîne un modèle de régression pour prédire la durée d'hospitalisation
    
    Args:
        data: DataFrame contenant les données d'entraînement
        target_col: Nom de la colonne cible (durée moyenne d'hospitalisation)
        fold: Nombre de folds pour la validation croisée
        experiment_name: Nom de l'expérience MLflow
    
    Returns:
        Le meilleur modèle entraîné et les encodeurs utilisés
    """
    # Préparer les données
    prepared_data, encoders = prepare_duration_data(data)
    
    # Configurer MLflow
    mlflow.set_experiment(experiment_name)
    
    # Setup PyCaret
    reg_setup = setup(
        data=prepared_data,
        target=target_col,
        session_id=123,
        fold=fold,
        log_experiment=False,
        experiment_name=experiment_name,
        feature_selection=True,
        remove_multicollinearity=True,
        normalize=True,
        transformation=True,
    )
    
    # Comparer différents modèles
    best_model = compare_models(n_select=1)
    
    # Tuner le meilleur modèle
    tuned_model = tune_model(best_model)
    
    # Log du modèle et des métriques avec MLflow
    with mlflow.start_run():
        # Log des paramètres
        mlflow.log_params(tuned_model.get_params())
        
        # Log du modèle
        mlflow.pycaret.log_model(tuned_model, "duration_predictor")
        
        # Log des métriques de performance
        results = pull()
        for metric in results.columns[1:]:
            mlflow.log_metric(metric, results.iloc[0][metric])
        
        # Log des encodeurs
        mlflow.log_dict(
            {k: v.classes_.tolist() for k, v in encoders.items()},
            "label_encoders.json"
        )
    
    return tuned_model, encoders

def load_duration_predictor(run_id: str) -> Tuple[Optional[object], Optional[Dict]]:
    """
    Charge un modèle de prédiction de durée depuis MLflow
    
    Args:
        run_id: ID MLflow du run contenant le modèle
    
    Returns:
        Le modèle chargé et les encodeurs, ou None si le chargement échoue
    """
    try:
        model = mlflow.pycaret.load_model(f"runs:/{run_id}/duration_predictor")
        encoders = mlflow.load_dict(f"runs:/{run_id}/label_encoders.json")
        return model, encoders
    except Exception as e:
        print(f"Erreur lors du chargement du modèle: {str(e)}")
        return None, None
