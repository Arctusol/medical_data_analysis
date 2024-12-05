import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.cloud import bigquery
from pygwalker.api.streamlit import StreamlitRenderer

# Fonction de chargement des données
@st.cache_resource
def load_data():
    try:
        gcp_service_account = st.secrets["gcp_service_account"]
        client = bigquery.Client.from_service_account_info(gcp_service_account)
        
        query = '''
            SELECT *
            FROM `projet-jbn-data-le-wagon.dbt_medical_analysis_join_total_morbidite.class_join_total_morbidite_sexe_population`
            WHERE sexe != 'Ensemble'
        '''
        df = client.query(query).to_dataframe()
        
        # Conversion des types de données pour optimisation
        date_columns = ['year']
        numeric_columns = [col for col in df.columns if any(x in col.lower() for x in ['hospi', 'tx_', 'lit_', 'place_', 'evolution'])]
        
        for col in date_columns:
            df[col] = pd.to_datetime(df[col]).dt.date
        for col in numeric_columns:
            df[col] = df[col].astype('float32')
            
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {str(e)}")
        return None

# Chargement initial des données
df_main = load_data()

if df_main is not None:
    # Création des vues spécifiques
    @st.cache_data
    def create_specific_views(df):
        # Vue Hospitalisations de base
        df_hospi_base = df[[
            'year', 'region', 'nom_region', 'sexe', 'pathologie', 'nom_pathologie',
            'nbr_hospi', 'hospi_prog_24h', 'hospi_autres_24h', 'hospi_total_24h'
        ]].copy()
        
        # Vue Durées d'hospitalisation
        df_duree = df[[
            'year', 'region', 'nom_region', 'sexe', 'pathologie', 'nom_pathologie',
            'AVG_duree_hospi', 'hospi_1J', 'hospi_2J', 'hospi_3J', 'hospi_4J',
            'hospi_5J', 'hospi_6J', 'hospi_7J', 'hospi_8J', 'hospi_9J',
            'hospi_10J_19J', 'hospi_20J_29J', 'hospi_30J'
        ]].copy()
        
        # Vue Taux et population
        df_taux = df[[
            'year', 'region', 'nom_region', 'sexe', 'pathologie', 'nom_pathologie',
            'tx_brut_tt_age_pour_mille', 'tx_standard_tt_age_pour_mille',
            'population'
        ]].copy()
        
        # Vue Évolutions
        df_evolution = df[[
            'year', 'region', 'nom_region', 'pathologie', 'nom_pathologie',
            'evolution_nbr_hospi', 'evolution_percent_nbr_hospi',
            'evolution_hospi_total_24h', 'evolution_hospi_total_jj',
            'evolution_AVG_duree_hospi'
        ]].copy()
        
        return df_hospi_base, df_duree, df_taux, df_evolution

    # Création des vues
    df_hospi_base, df_duree, df_taux, df_evolution = create_specific_views(df_main)

    # Add Title
    st.markdown("<h1 class='main-title' style='margin-top: -50px;'>📊 Générateur de Graphiques</h1>", unsafe_allow_html=True)

    # Options de visualisation
    st.sidebar.title("Options de Visualisation")
    viz_type = st.sidebar.selectbox(
        "Type de visualisation",
        ["PyGWalker", "Graphiques Personnalisés"]
    )

    if viz_type == "PyGWalker":
        # Création des onglets pour chaque vue
        tab_hospi, tab_duree, tab_taux, tab_evolution = st.tabs([
            "Hospitalisations", "Durées de séjour", "Taux et population", 
            "Évolutions"
        ])

        with tab_hospi:
            st.header("Données d'hospitalisation de base")
            walker_hospi = StreamlitRenderer(df_hospi_base, spec="./config.json", spec_io_mode="json_file")
            walker_hospi.explorer()

        with tab_duree:
            st.header("Durées d'hospitalisation")
            walker_duree = StreamlitRenderer(df_duree, spec="./config.json", spec_io_mode="json_file")
            walker_duree.explorer()

        with tab_taux:
            st.header("Taux et population")
            walker_taux = StreamlitRenderer(df_taux, spec="./config.json", spec_io_mode="json_file")
            walker_taux.explorer()

        with tab_evolution:
            st.header("Évolutions des indicateurs")
            walker_evolution = StreamlitRenderer(df_evolution, spec="./config.json", spec_io_mode="json_file")
            walker_evolution.explorer()

    else:
        # Menu déroulant pour sélectionner le type de graphique
        chart_type = st.sidebar.selectbox(
            "Type de graphique",
            ["Hospitalisations", "Durées", "Taux", "Évolutions"]
        )

        # Filtres communs
        selected_year = st.sidebar.selectbox("Année", sorted(df_main['year'].unique()))
        selected_region = st.sidebar.multiselect("Régions", df_main['nom_region'].unique())
        selected_path = st.sidebar.multiselect("Pathologies", df_main['nom_pathologie'].unique())

        if selected_region and selected_path:
            if chart_type == "Hospitalisations":
                filtered_df = df_hospi_base[
                    (df_hospi_base['year'] == selected_year) &
                    (df_hospi_base['nom_region'].isin(selected_region)) &
                    (df_hospi_base['nom_pathologie'].isin(selected_path))
                ]
                
                fig = px.bar(filtered_df, 
                           x='nom_region',
                           y=['hospi_prog_24h', 'hospi_autres_24h'],
                           title='Répartition des hospitalisations par type',
                           barmode='group')
                st.plotly_chart(fig)

            elif chart_type == "Durées":
                filtered_df = df_duree[
                    (df_duree['year'] == selected_year) &
                    (df_duree['nom_region'].isin(selected_region)) &
                    (df_duree['nom_pathologie'].isin(selected_path))
                ]
                
                duree_cols = ['hospi_1J', 'hospi_2J', 'hospi_3J', 'hospi_4J', 'hospi_5J',
                             'hospi_6J', 'hospi_7J', 'hospi_8J', 'hospi_9J',
                             'hospi_10J_19J', 'hospi_20J_29J', 'hospi_30J']
                
                fig = px.bar(filtered_df.melt(value_vars=duree_cols),
                            x='variable', y='value',
                            color='nom_region',
                            title='Distribution des durées d\'hospitalisation')
                st.plotly_chart(fig)

            elif chart_type == "Taux":
                filtered_df = df_taux[
                    (df_taux['year'] == selected_year) &
                    (df_taux['nom_region'].isin(selected_region)) &
                    (df_taux['nom_pathologie'].isin(selected_path))
                ]
                
                fig = px.scatter(filtered_df,
                               x='tx_brut_tt_age_pour_mille',
                               y='tx_standard_tt_age_pour_mille',
                               color='nom_region',
                               size='population',
                               hover_data=['nom_pathologie'],
                               title='Comparaison des taux bruts et standardisés')
                st.plotly_chart(fig)

            else:  # Évolutions
                filtered_df = df_evolution[
                    (df_evolution['year'] == selected_year) &
                    (df_evolution['nom_region'].isin(selected_region)) &
                    (df_evolution['nom_pathologie'].isin(selected_path))
                ]
                
                fig = px.bar(filtered_df,
                           x='nom_region',
                           y=['evolution_percent_nbr_hospi', 'evolution_AVG_duree_hospi'],
                           title='Évolution des indicateurs clés (%)',
                           barmode='group')
                st.plotly_chart(fig)
        else:
            st.info("Veuillez sélectionner au moins une région et une pathologie")

else:
    st.error("Erreur lors du chargement des données. Veuillez réessayer.")

st.markdown("---")
st.markdown("Développé avec 💫| Le Wagon - Batch #1834 - Promotion 2024")
