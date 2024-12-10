import os
from google.cloud import bigquery
import pandas as pd
from typing import Dict, Tuple
from sklearn.model_selection import train_test_split

def load_data() -> Dict[str, pd.DataFrame]:
    """
    Charge les données depuis BigQuery, à la fois la table de morbidité et la table des capacités
    """
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "projet-jbn-data-le-wagon-533639ce801d.json"
    client = bigquery.Client()

    # Table de morbidité
    query_morbidite = """
    SELECT * FROM projet-jbn-data-le-wagon.dbt_medical_analysis_join_total_morbidite.class_join_total_morbidite_sexe_population
    """
    
    # Table des capacités
    query_capacite = """
    SELECT * FROM projet-jbn-data-le-wagon.dbt_medical_analysis_join_total_morbidite_capacite.class_join_total_morbidite_capacite_kpi
    """

    df_morbidite = client.query(query_morbidite).to_dataframe()
    df_capacite = client.query(query_capacite).to_dataframe()

    return {
        'morbidite': df_morbidite,
        'capacite': df_capacite
    }

def prepare_datasets(df_morbidite: pd.DataFrame, df_capacite: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Prépare les différents ensembles de données pour l'entraînement et le test
    """
    # Filtrer les données de morbidité pour "ensemble" uniquement
    df_morbidite = df_morbidite[df_morbidite["sexe"] == "Ensemble"]
    
    # Filtrer par niveau
    df_hospi_dpt = df_morbidite[df_morbidite["niveau"] == "Départements"]
    df_hospi_reg = df_morbidite[df_morbidite["niveau"] == "Régions"]

    # Filtrer par année
    df_hospi_dpt_yr = df_hospi_dpt[df_hospi_dpt["annee"].isin([2018, 2019, 2022])]
    df_hospi_reg_yr = df_hospi_reg[df_hospi_reg["annee"].isin([2018, 2019, 2022])]

    # Filtrer les données de capacité
    df_capacite_yr = df_capacite[df_capacite["annee"].isin([2018, 2019, 2022])]

    return {
        'dpt': df_hospi_dpt_yr,
        'reg': df_hospi_reg_yr,
        'capacite': df_capacite_yr
    }

def prepare_train_test_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Sépare les données en ensembles d'entraînement (2018-2019) et de test (2022)
    """
    train_data = df[df['annee'].isin([2018, 2019])]
    test_data = df[df['annee'] == 2022]
    
    return train_data, test_data

def prepare_features_for_service_classification(df_morbidite: pd.DataFrame, df_capacite: pd.DataFrame) -> pd.DataFrame:
    """
    Prépare les features pour la classification des services
    """
    # Fusionner les données de morbidité et de capacité
    features_df = pd.merge(
        df_morbidite,
        df_capacite,
        on=['code_geo', 'annee', 'niveau'],
        how='left'
    )

    # Sélectionner les colonnes pertinentes
    selected_columns = [
        'code_geo', 'annee', 'niveau',
        'taux_standardise', 'nombre_sejours',
        'nombre_journees', 'duree_moyenne_sejour',
        'capacite_lits', 'taux_occupation',
        'service'  # target variable
    ]

    return features_df[selected_columns]

def prepare_features_for_duration_prediction(df_morbidite: pd.DataFrame, df_capacite: pd.DataFrame) -> pd.DataFrame:
    """
    Prépare les features pour la prédiction de la durée d'hospitalisation
    """
    # Fusionner les données de morbidité et de capacité
    features_df = pd.merge(
        df_morbidite,
        df_capacite,
        on=['code_geo', 'annee', 'niveau'],
        how='left'
    )

    # Sélectionner les colonnes pertinentes
    selected_columns = [
        'code_geo', 'annee', 'niveau',
        'taux_standardise', 'nombre_sejours',
        'capacite_lits', 'taux_occupation',
        'service',
        'duree_moyenne_sejour'  # target variable
    ]

    return features_df[selected_columns]
