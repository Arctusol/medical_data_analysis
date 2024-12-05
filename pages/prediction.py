import streamlit as st
import pandas as pd
import numpy as np
from pycaret.regression import *
from google.cloud import bigquery
import os
import plotly.express as px

# Configuration de la page
st.set_page_config(page_title="Prédiction des hospitalisations", layout="wide")

# Titre de la page
st.title(" Prédiction des hospitalisations")

# Sidebar pour les filtres
st.sidebar.header("Paramètres de prédiction")

# Connexion à BigQuery
@st.cache_resource
def init_bigquery():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/antob/Documents/Arctusol/projet_wagon/projet_data_JBN/projet-jbn-data-le-wagon-533639ce801d.json"
    return bigquery.Client()

# Chargement des données
@st.cache_data
def load_data():
    client = init_bigquery()
    query = """
    SELECT * FROM projet-jbn-data-le-wagon.dbt_medical_analysis_join_total_morbidite.class_join_total_morbidite_sexe_population
    """
    return client.query(query).to_dataframe()

# Chargement du modèle
@st.cache_resource
def load_saved_model():
    # Préparation des données d'entraînement (2018-2019)
    train_data = df[(df['niveau'] == 'Régions') & 
                    (df['sexe'] == 'Ensemble') & 
                    (df['annee'].isin([2018, 2019]))]
    
    # Sélection des variables pertinentes
    features = ['annee', 'nom_pathologie', 'nom_region']
    train_data = train_data[features + ['nbr_hospi']]
    
    # Initialisation de l'environnement PyCaret
    reg = setup(
        data=train_data,
        target='nbr_hospi',
        session_id=123,
        normalize=True,
        transformation=True,
        ignore_features=['annee'],
        fold=5,
        verbose=False
    )
    
    # Chargement du modèle sauvegardé
    return load_model('best_model')

try:
    # Chargement des données
    df = load_data()
    
    # Filtres pour les prédictions
    regions = sorted(df[df['niveau'] == 'Régions']['nom_region'].unique())
    selected_region = st.sidebar.selectbox('Sélectionnez une région', regions)
    
    pathologies = sorted(df['nom_pathologie'].unique())
    selected_pathology = st.sidebar.selectbox('Sélectionnez une pathologie', pathologies)
    
    selected_year = st.sidebar.slider('Année de prédiction', 2023, 2026, 2023)

    # Création des données pour toutes les prédictions futures
    future_years = list(range(2023, selected_year + 1))
    input_data = pd.DataFrame([{
        'annee': year,
        'nom_pathologie': selected_pathology,
        'nom_region': selected_region
    } for year in future_years])

    # Bouton pour lancer la prédiction
    if st.sidebar.button('Faire une prédiction'):
        # Chargement du modèle et prédiction
        with st.spinner('Chargement du modèle et calcul des prédictions...'):
            model = load_saved_model()
            all_predictions = predict_model(model, data=input_data)
        
        # Affichage des résultats
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Résultats de la prédiction")
            st.metric(
                label="Nombre d'hospitalisations prévu",
                value=f"{int(all_predictions[all_predictions['annee'] == selected_year]['prediction_label'].iloc[0]):,}"
            )
            
        with col2:
            st.subheader("Informations")
            st.write(f"**Région:** {selected_region}")
            st.write(f"**Pathologie:** {selected_pathology}")
            st.write(f"**Année:** {selected_year}")

        # Affichage des données historiques
        st.subheader("Historique des hospitalisations")
        historical_data = df[
            (df['nom_region'] == selected_region) & 
            (df['nom_pathologie'] == selected_pathology) &
            (df['niveau'] == 'Régions') &
            (df['sexe'] == 'Ensemble')
        ]
        
        # Création du graphique avec les données historiques
        fig = px.line(historical_data, x='annee', y='nbr_hospi', 
                     title=f"Évolution des hospitalisations - {selected_pathology} en {selected_region}")
        
        # Obtenir la dernière valeur historique (2022)
        last_historical = historical_data[historical_data['annee'] == 2022]['nbr_hospi'].iloc[0]
        
        # Créer la ligne de projection avec toutes les prédictions
        projection_x = [2022] + all_predictions['annee'].tolist()
        projection_y = [last_historical] + all_predictions['prediction_label'].tolist()
        
        # Ajouter la ligne de projection
        fig.add_scatter(
            x=projection_x,
            y=projection_y,
            mode='lines',
            name='Projection',
            line=dict(dash='dash', color='red'),
            showlegend=True
        )
        
        # Ajouter les points de prédiction
        fig.add_scatter(
            x=all_predictions['annee'],
            y=all_predictions['prediction_label'],
            mode='markers',
            name='Prédictions',
            marker=dict(size=10, color='red'),
            showlegend=True
        )
        
        # Mise en forme du graphique
        fig.update_layout(
            xaxis_title="Année",
            yaxis_title="Nombre d'hospitalisations",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Une erreur s'est produite : {str(e)}")

st.markdown("---")
st.markdown("Développé avec 💫| Le Wagon - Batch #1834 - Promotion 2024")
