from pycaret.classification import *
import mlflow
import pandas as pd
from typing import Optional, Tuple, Dict
from sklearn.preprocessing import LabelEncoder

def prepare_service_data(data: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """
    Prépare les données pour la classification des services
    
    Args:
        data: DataFrame contenant les données brutes
        
    Returns:
        DataFrame préparé et dictionnaire des encodeurs
    """
    # Sélectionner les colonnes pertinentes
    features = [
        'pathologie', 'code_pathologie', 'nom_pathologie',
        'tranche_age_0_1', 'tranche_age_1_4', 'tranche_age_5_14',
        'tranche_age_15_24', 'tranche_age_25_34', 'tranche_age_35_44',
        'tranche_age_45_54', 'tranche_age_55_64', 'tranche_age_65_74',
        'tranche_age_75_84', 'tranche_age_85_et_plus',
        'tx_brut_tt_age_pour_mille', 'tx_standard_tt_age_pour_mille',
        'classification'  # target variable
    ]
    
    df = data[features].copy()
    
    # Créer les encodeurs pour les variables catégorielles
    encoders = {}
    categorical_features = ['pathologie', 'nom_pathologie', 'classification']
    
    for feature in categorical_features:
        encoders[feature] = LabelEncoder()
        df[feature] = encoders[feature].fit_transform(df[feature])
    
    return df, encoders

def train_service_classifier(
    data: pd.DataFrame,
    target_col: str = 'classification',
    fold: int = 5,
    experiment_name: str = 'service_classification'
) -> Tuple[object, Dict]:
    """
    Entraîne un modèle de classification pour prédire le service médical approprié
    
    Args:
        data: DataFrame contenant les données d'entraînement
        target_col: Nom de la colonne cible (service médical)
        fold: Nombre de folds pour la validation croisée
        experiment_name: Nom de l'expérience MLflow
    
    Returns:
        Le meilleur modèle entraîné et les encodeurs utilisés
    """
    try:
        # Préparer les données
        prepared_data, encoders = prepare_service_data(data)
        
        # Setup PyCaret sans MLflow
        clf_setup = setup(
            data=prepared_data,
            target=target_col,
            session_id=123,
            fold=fold,
            log_experiment=False,  # Désactiver l'intégration MLflow de PyCaret
            verbose=False
        )
        
        # Entraîner le modèle
        best_model = compare_models(n_select=1)
        
        # Log manuel avec MLflow
        mlflow.set_experiment(experiment_name)
        with mlflow.start_run():
            # Log des paramètres de base
            mlflow.log_param("target_col", target_col)
            mlflow.log_param("fold", fold)
            
            # Log des métriques de performance
            results = pull()
            for metric in results.columns[1:]:
                mlflow.log_metric(metric, results.iloc[0][metric])
        
        return best_model, encoders
            
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'entraînement : {str(e)}")
        raise

def load_service_classifier(run_id: str) -> Tuple[Optional[object], Optional[Dict]]:
    """
    Charge un modèle de classification de service depuis MLflow
    
    Args:
        run_id: ID MLflow du run contenant le modèle
    
    Returns:
        Le modèle chargé et les encodeurs, ou None si le chargement échoue
    """
    try:
        model = mlflow.pycaret.load_model(f"runs:/{run_id}/service_classifier")
        encoders = mlflow.load_dict(f"runs:/{run_id}/label_encoders.json")
        return model, encoders
    except Exception as e:
        print(f"Erreur lors du chargement du modèle: {str(e)}")
        return None, None
