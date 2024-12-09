import streamlit as st
import pandas as pd
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
        numeric_columns = [col for col in df.columns if any(x in col.lower() for x in ['hospi'])]
        
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
    # Création de la vue spécifique
    @st.cache_data
    def create_specific_view(df):
        # Vue Hospitalisations de base
        return df[[
            'year', 'region', 'nom_region', 'sexe', 'pathologie', 'nom_pathologie',
            'nbr_hospi', 'hospi_prog_24h', 'hospi_autres_24h', 'hospi_total_24h'
        ]].copy()

    # Création de la vue
    df_hospi_base = create_specific_view(df_main)

    # Add Title
    st.markdown("<h1 class='main-title' style='margin-top: -50px;'>📊 Générateur de Graphiques</h1>", unsafe_allow_html=True)

    # Affichage du tableau avec PyGWalker
    st.header("Données d'hospitalisation")
    walker_hospi = StreamlitRenderer(df_hospi_base, spec="./config.json", spec_io_mode="json_file")
    walker_hospi.explorer()

else:
    st.error("Erreur lors du chargement des données. Veuillez réessayer.")

st.markdown("---")
st.markdown("Développé avec 💫| Le Wagon - Batch #1834 - Promotion 2024")
