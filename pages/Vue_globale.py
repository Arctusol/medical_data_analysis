import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from google.cloud import bigquery
from streamlit_extras.metric_cards import style_metric_cards 
import time
import folium
from streamlit_folium import st_folium
import json
from pygwalker.api.streamlit import StreamlitRenderer
import pygwalker as pyg
from langchain_openai import AzureChatOpenAI
import numpy as np


# Styles CSS personnalisés
st.markdown("""
<style>
    .stApp {
        background-color: #ffffff;
    }
    .main-title {
        color: #2c3e50;
        text-align: center;
        padding: 1rem 0;
        font-size: 2.5rem;
    }
    .section-title {
        color: #34495e;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
        margin: 2rem 0 1rem 0;
    }
    .insight-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    .metric-container {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin: 0.5rem 0;
    }
    .tab-content {
        padding: 1rem;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Définition des couleurs du thème
MAIN_COLOR = '#003366'  # Bleu marine principal
SECONDARY_COLOR = '#AFDC8F'  # Vert clair complémentaire
ACCENT_COLOR = '#3D7317'  # Vert foncé pour les accents

# Fonction de chargement des données avec gestion d'erreurs
@st.cache_resource
def fetch_data():
    try:
        # Chargement des secrets
        gcp_service_account = st.secrets["gcp_service_account"]
        client = bigquery.Client.from_service_account_info(gcp_service_account)
        
        # Chargement du dataset principal qui contient toutes les données
        df_complet = client.query('''
            SELECT * FROM `projet-jbn-data-le-wagon.dbt_medical_analysis_join_total_morbidite.class_join_total_morbidite_sexe_population`
        ''').to_dataframe()
        
        # Convertir les colonnes year en datetime
        df_complet['year'] = pd.to_datetime(df_complet['year'])
        
        # Créer des vues spécifiques pour maintenir la compatibilité avec le code existant
        df_nbr_hospi = df_complet[[
            'niveau', 'year', 'region', 'nom_region', 'pathologie', 'nom_pathologie', 'sexe',
            'nbr_hospi', 'evolution_nbr_hospi', 'evolution_percent_nbr_hospi','hospi_prog_24h','hospi_autres_24h','hospi_total_24h',
            'hospi_1J','hospi_2J','hospi_3J','hospi_4J','hospi_5J','hospi_6J','hospi_7J','hospi_8J','hospi_9J','hospi_10J_19J','hospi_20J_29J',
            'hospi_30J','hospi_total_jj','total_hospi','evolution_hospi_total_24h','evolution_percent_hospi_total_24h','evolution_hospi_total_jj',
            'evolution_percent_hospi_total_jj','evolution_total_hospi','evolution_percent_total_hospi','evolution_hospi_total_24h', 'evolution_hospi_total_jj',
            'indice_comparatif_tt_age_percent',
            'tranche_age_0_1', 'tranche_age_1_4', 'tranche_age_5_14',
            'tranche_age_15_24', 'tranche_age_25_34', 'tranche_age_35_44',
            'tranche_age_45_54', 'tranche_age_55_64', 'tranche_age_65_74',
            'tranche_age_75_84', 'tranche_age_85_et_plus','classification',
        ]].copy()

        df_duree_hospi = df_complet[[
            'niveau','year', 'region', 'nom_region', 'pathologie', 'nom_pathologie', 'sexe',
            'AVG_duree_hospi', 'evolution_AVG_duree_hospi', 'evolution_percent_AVG_duree_hospi',
            'evolution_hospi_total_jj','classification',
        ]].copy()

        df_tranche_age_hospi = df_complet[[
            'niveau','year', 'region', 'nom_region', 'pathologie', 'nom_pathologie',
            'tranche_age_0_1', 'tranche_age_1_4', 'tranche_age_5_14',
            'tranche_age_15_24', 'tranche_age_25_34', 'tranche_age_35_44',
            'tranche_age_45_54', 'tranche_age_55_64', 'tranche_age_65_74',
            'tranche_age_75_84', 'tranche_age_85_et_plus',
            'tx_brut_tt_age_pour_mille', 'tx_standard_tt_age_pour_mille',
            'indice_comparatif_tt_age_percent','classification'
        ]].copy()
        
        # Charger uniquement les données de capacité
        df_capacite_hospi = client.query('''
            SELECT * FROM `projet-jbn-data-le-wagon.dbt_medical_analysis_join_total_morbidite_capacite.class_join_total_morbidite_capacite`
        ''').to_dataframe()
        
        # Convertir la colonne year en datetime pour df_capacite_hospi
        df_capacite_hospi['year'] = pd.to_datetime(df_capacite_hospi['year'])
        
        return df_nbr_hospi, df_duree_hospi, df_tranche_age_hospi, df_capacite_hospi, df_complet
        
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {str(e)}")
        return None, None, None, None, None

# Fonction pour calculer les métriques de la page principale
@st.cache_data
def calculate_main_metrics(df_nbr_hospi, df_capacite_hospi, selected_sex='Ensemble'):
    metrics = {}
    
    # Calcul des hospitalisations par année
    df_hospi_filtered = df_nbr_hospi[(df_nbr_hospi['sexe'] == selected_sex) & (df_nbr_hospi['niveau'] == 'Départements')]
    for year in range(2018, 2023):
        total_hospi = df_hospi_filtered["nbr_hospi"][df_hospi_filtered["year"].dt.year == year].sum()
        metrics[f"hospi_{year}"] = total_hospi

    # Calcul des lits disponibles par année
    df_capacite_filtered = df_capacite_hospi[df_capacite_hospi['niveau'] == 'Départements']
    lits_disponibles = df_capacite_filtered.groupby('year')['lit_hospi_complete'].sum().reset_index()
    for year in range(2018, 2023):
        metrics[f"lits_{year}"] = lits_disponibles[lits_disponibles['year'].dt.year == year]['lit_hospi_complete'].sum()
    
    return metrics

# Interface de chargement
def load_with_progress():
    # Centrer le GIF avec du CSS personnalisé
    st.markdown("""
        <style>
        .loading-gif {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Créer un conteneur pour le GIF centré
    gif_container = st.container()
    with gif_container:
        st.markdown('<div class="loading-gif">', unsafe_allow_html=True)
        gif_placeholder = st.empty()
        gif_placeholder.image("ezgif.com-crop.gif", width=300)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Créer la barre de progression séparément
    progress_container = st.container()
    with progress_container:
        progress_bar = st.progress(0, text="Initialisation du chargement...")
    
    try:
        # Chargement des données
        progress_bar.progress(10, text="Chargement des données...")
        df_nbr_hospi, df_duree_hospi, df_tranche_age_hospi, df_capacite_hospi, df_complet = fetch_data()
        
        if df_complet is None:
            gif_placeholder.empty()
            progress_bar.empty()
            st.stop()
        
        # Calcul des métriques
        progress_bar.progress(80, text="Calcul des métriques...")
        metrics = calculate_main_metrics(df_nbr_hospi, df_capacite_hospi, 'Ensemble')
        
        progress_bar.progress(100, text="Chargement terminé!")
        time.sleep(0.5)
        
        # Clear loading interface
        gif_placeholder.empty()
        progress_bar.empty()
        
        return df_nbr_hospi, df_duree_hospi, df_tranche_age_hospi, df_capacite_hospi, df_complet, metrics
        
    except Exception as e:
        gif_placeholder.empty()
        progress_bar.empty()
        st.error(f"Erreur inattendue: {str(e)}")
        st.stop()

def format_number(number):
    """Format un nombre en K ou M selon sa taille"""
    try:
        num = float(str(number).replace(',', ''))
        if num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        else:
            return f"{num:.0f}"
    except (ValueError, TypeError):
        return str(number)
# Chargement des données avec interface de progression
df_nbr_hospi, df_duree_hospi, df_tranche_age_hospi, df_capacite_hospi, df_complet, main_metrics = load_with_progress()

# Titre principal avec style amélioré
st.markdown("<h1 class='main-title' style='margin-top: -70px;'>🌍 Analyse hospitalière en France de 2018 à 2022</h1>", unsafe_allow_html=True)

# Suite du code uniquement si les données sont chargées correctement
if df_nbr_hospi is not None:
    # Filtres dans une card dédiée
    
    col1, col2, col3 = st.columns(3)

    with col1:
        # Sélection du niveau administratif
        niveau_administratif = st.selectbox(
            "Niveau administratif",
            ["Régions", "Départements"],
            key="niveau_administratif"
        )

    with col2:
        # Sélection du sexe
        selected_sex = st.selectbox(
            "Sexe",
            ["Ensemble", "Homme", "Femme"],
            key="selecteur_sexe"
        )

    with col3:
        # Filtre années avec une liste déroulante simple
        years = sorted(df_nbr_hospi['year'].dt.year.unique(), reverse=True)
        years_options = ["Toutes les années"] + [str(year) for year in years]
        selected_year = st.selectbox("Année", years_options, key="year_filter")
        
        # Convertir la sélection en liste d'années pour le filtrage
        if selected_year == "Toutes les années":
            selected_years = years
        else:
            selected_years = [int(selected_year)]

    # Sidebar pour la navigation
    st.sidebar.header("Navigation")
    
    # Filtrer le DataFrame en fonction du niveau sélectionné
    df_filtered = df_complet[df_complet['niveau'] == niveau_administratif]

    # Filtre régions/départements selon le niveau choisi
    territories = sorted(df_filtered['nom_region'].unique())
    territory_label = "régions" if niveau_administratif == "Régions" else "départements"
    
    select_all_territories = st.sidebar.checkbox(f"Sélectionner tous les {territory_label}", value=True)
    if select_all_territories:
        selected_territories = st.sidebar.multiselect(
            f"Sélectionner les {territory_label}",
            territories,
            default=territories
        )
    else:
        selected_territories = st.sidebar.multiselect(f"Sélectionner les {territory_label}", territories)
    
    # Appliquer les filtres aux DataFrames
    df_nbr_hospi_filtered = df_nbr_hospi[
        (df_nbr_hospi['year'].dt.year.isin(selected_years)) &
        (df_nbr_hospi['nom_region'].isin(selected_territories)) &
        (df_nbr_hospi['niveau'] == niveau_administratif) &
        (df_nbr_hospi['sexe'] == selected_sex)
    ]
    df_duree_hospi_filtered = df_duree_hospi[
        (df_duree_hospi['year'].dt.year.isin(selected_years)) &
        (df_duree_hospi['nom_region'].isin(selected_territories)) &
        (df_duree_hospi['niveau'] == niveau_administratif) &
        (df_duree_hospi['sexe'] == selected_sex)
    ]
    df_tranche_age_hospi_filtered = df_tranche_age_hospi[
        (df_tranche_age_hospi['year'].dt.year.isin(selected_years)) &
        (df_tranche_age_hospi['nom_region'].isin(selected_territories)) &
        (df_tranche_age_hospi['niveau'] == niveau_administratif)
    ]
    df_capacite_hospi_filtered = df_capacite_hospi[
        (df_capacite_hospi['year'].dt.year.isin(selected_years)) &
        (df_capacite_hospi['nom_region'].isin(selected_territories)) &
        (df_capacite_hospi['niveau'] == niveau_administratif)
    ]
    
    # Calcul des métriques principales avec le filtre de sexe sélectionné
    main_metrics = calculate_main_metrics(df_nbr_hospi, df_capacite_hospi, selected_sex)
    
    # Onglets principaux
    tab1, tab2, tab3, tab4, tab5= st.tabs([
        "📈 Vue générale",
        "🗺️ Analyse géographique",
        "🏥 Pathologies",
        "👥 Démographie",
        "🏥 Services Médicaux"

    ])
    
    # Vue Générale
    with tab1:        
        # Affichage des métriques dans des cartes stylisées
        col1, col2 = st.columns(2)
        
        with col1:
            value_2018 = main_metrics["hospi_2018"]
            value_2022 = main_metrics["hospi_2022"]
            value_2022_2018 = value_2022 - value_2018
            delta_total = ((value_2022 - value_2018) / value_2018) * 100
            
            st.markdown(f"""
                <div class="insight-card" style="background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); min-width: 400px;">
                    <h3 style="color: #333; font-size: 1.2rem; margin-bottom: 15px; white-space: nowrap; text-align: center;">Évolution des hospitalisations</h3>
                    <div style="display: flex; justify-content: center; gap: 40px;">
                        <div style="flex: 0 1 auto; text-align: center;">
                            <div style="font-size: 0.9rem; color: #666;">Nomber d'hospitalisations en 2022</div>
                            <div style="font-size: 2.5rem; margin: 5px 0;">{value_2022 / 1_000_000:.2f}M</div>
                        </div>
                        <div style="flex: 0 1 auto; text-align: center;">
                            <div style="font-size: 0.9rem; color: #666;">Évolution 2018-2022</div>
                            <div style="font-size: 2.5rem; margin: 5px 0;">+{value_2022_2018 / 1_000:.2f}K</div>
                            <div style="color: #2fba3d; font-size: 0.9rem;">↑ {delta_total:.2f}% vs 2018</div>
                        </div>
                    </div>
                </div>  
            """, unsafe_allow_html=True)
            
        with col2:
            value_2018_lits = main_metrics["lits_2018"]
            value_2019_lits = main_metrics["lits_2019"]
            value_2022_lits = main_metrics["lits_2022"]
            lits_perdus = value_2018_lits - value_2022_lits
            delta_total_lits = ((value_2022_lits - value_2018_lits) / value_2018_lits) * 100

            st.markdown(f"""
                <div class="insight-card" style="background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); min-width: 400px;">
                    <h3 style="color: #333; font-size: 1.2rem; margin-bottom: 15px; white-space: nowrap; text-align: center;">Évolution de la capacité en lit</h3>
                    <div style="display: flex; justify-content: center; gap: 40px;">
                        <div style="flex: 0 1 auto; text-align: center;">
                            <div style="font-size: 0.9rem; color: #666;">Nombe de lits disponible en 2022</div>
                            <div style="font-size: 2.5rem; margin: 5px 0;">{value_2022_lits / 1_000:.2f}K</div>
                        </div>
                        <div style="flex: 0 1 auto; text-align: center;">
                            <div style="font-size: 0.9rem; color: #666;">Évolution 2018-2022</div>
                            <div style="font-size: 2.5rem; margin: 5px 0;">-{lits_perdus / 1_000:.2f}K</div>
                            <div style="color: #d63b18; font-size: 0.9rem;">↓ {delta_total_lits:.2f}% vs 2018</div>
                        </div>
                    </div>
                </div>  
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        # Affichage des lits disponibles

        # Graph 1 Préparation des données
        hospi_by_year = df_nbr_hospi_filtered.groupby('year')['nbr_hospi'].sum().reset_index()
        duree_by_year = df_duree_hospi_filtered.groupby('year')['AVG_duree_hospi'].mean().reset_index()

        capacite_by_year = df_capacite_hospi_filtered.groupby('year')[['lit_hospi_complete','place_hospi_partielle','passage_urgence']].sum().reset_index()
        capacite_by_year['capacite_totale'] = capacite_by_year['lit_hospi_complete'] + capacite_by_year['place_hospi_partielle']

        # Création du graphique pour les barres
        fig = px.bar(
            data_frame=pd.concat([
                hospi_by_year.assign(Type="Nombre d'hospitalisations", value=lambda x: x['nbr_hospi']),
            ]),
            x='year',
            y='value',
            color='Type',
            barmode='group',
            color_discrete_map={
                "Nombre d'hospitalisations": MAIN_COLOR,
                "Capacité en Lits (>24h)": SECONDARY_COLOR
            }
        )

        # Ajout de la ligne pour la durée moyenne
        fig.add_scatter(
            x=duree_by_year['year'],
            y=duree_by_year['AVG_duree_hospi'],
            name="Durée moyenne",
            yaxis='y2',
            line=dict(color=SECONDARY_COLOR, width=3),
            mode='lines+markers+text',
            text=duree_by_year['AVG_duree_hospi'].round(1),
            textposition='top center',
            hovertemplate="<b>Année:</b> %{x|%Y}<br><b>Durée moyenne:</b> %{y:.1f} jours<br><extra></extra>"
        )

        # Mise à jour de la mise en page
        fig.update_layout(
            title="Évolution des hospitalisations et de leur durée moyenne",
            yaxis=dict(
                title="Nombre d'hospitalisations et capacité",
                titlefont=dict(color=MAIN_COLOR),
                tickfont=dict(color=MAIN_COLOR),
                showgrid=True,
                range=[0, max(max(hospi_by_year['nbr_hospi']), max(capacite_by_year['capacite_totale'])) * 1.1]  # Ajuster l'échelle avec 10% de marge
            ),
            yaxis2=dict(
                title="Durée moyenne (jours)",
                titlefont=dict(color=ACCENT_COLOR),
                tickfont=dict(color=ACCENT_COLOR),
                anchor="x",
                overlaying="y",
                side="right"
            ),
            xaxis=dict(
                title="Année",
                tickformat="%Y"
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode='x unified',
            hoverlabel=dict(bgcolor="white"),
            template='plotly_white'
        )

        # Affichage du graphique
        col_chart, col_help = st.columns([1, 0.01])
        with col_chart:
            st.plotly_chart(fig, use_container_width=True)
        with col_help:
            st.metric(label="help", value="", help="Ce graphique combine le nombre total d'hospitalisations (barres bleues) et la durée moyenne de séjour (ligne verte) par année. Passez votre souris sur les éléments du graphique pour voir les détails.")
        
        # Graph 2 Préparation des données
        
        # Création du graphique pour les barres
        fig2 = px.bar(
            data_frame=pd.concat([
                capacite_by_year.assign(Type="Capacité en Lits (>24h)", value=lambda x: x['lit_hospi_complete']),
                capacite_by_year.assign(Type="Capacité en Places (<24h)", value=lambda x: x['place_hospi_partielle'])
            ]),
            x='year',
            y='value',
            color='Type',
            barmode='group',
            color_discrete_map={
                "Capacité en Lits (>24h)": SECONDARY_COLOR,
                "Capacité en Places (<24h)": ACCENT_COLOR
            }
        )

        # Ajout de la ligne pour les passages aux urgences
        fig2.add_scatter(
            x=capacite_by_year['year'],
            y=capacite_by_year['passage_urgence'],
            name="Passages aux urgences mesurés",
            yaxis='y2',
            line=dict(color=MAIN_COLOR, width=3),
            mode='lines+markers+text',
            text=capacite_by_year['passage_urgence'].round(0),
            textposition='top center',
            hovertemplate="<b>Année:</b> %{x|%Y}<br><b>Passages Urgences:</b> %{y:,.0f}<br><extra></extra>"
        )

        # Mise à jour de la mise en page
        fig2.update_layout(
            title="Évolution des capacités d'accueil et des passages aux urgences",
            yaxis=dict(
                title="Nombre de lits et places",
                titlefont=dict(color=SECONDARY_COLOR),
                tickfont=dict(color=SECONDARY_COLOR),
                showgrid=True
            ),
            yaxis2=dict(
                title="Nombre de passages aux urgences",
                titlefont=dict(color=MAIN_COLOR),
                tickfont=dict(color=MAIN_COLOR),
                anchor="x",
                overlaying="y",
                side="right"
            ),
            xaxis=dict(
                title="Année",
                tickformat="%Y"
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode='x unified',
            hoverlabel=dict(bgcolor="white"),
            template='plotly_white'
        )

        # Affichage du graphique
        col_chart, col_help = st.columns([1, 0.01])
        with col_chart:
            st.plotly_chart(fig2, use_container_width=True)
        with col_help:
            st.metric(label="help", value="", help="Ce graphique montre l'évolution des capacités d'accueil (barres) et des passages aux urgences (ligne). Les barres représentent la capacité en lits d'hospitalisation complète et en places d'hospitalisation partielle.")

    # Analyse Géographique
    with tab2:

        col1, col2 = st.columns(2)
        with col1:
            # Adapter le groupby selon le niveau administratif
            territory_col = 'nom_region'
            territory_label = "région" if niveau_administratif == "Régions" else "département"
            
            hospi_by_territory = df_nbr_hospi_filtered.groupby(territory_col)['nbr_hospi'].sum().reset_index()
            hospi_by_territory = hospi_by_territory.sort_values(by='nbr_hospi', ascending=True)
            
            fig = px.bar(hospi_by_territory, x='nbr_hospi', y=territory_col,
                        title=f'Nombre d\'hospitalisations par {territory_label}',
                        labels={'nbr_hospi': 'Nombre d\'hospitalisations',
                               territory_col: territory_label.capitalize()},
                        custom_data=[territory_col, 'nbr_hospi'],
                        orientation='h')
            fig.update_traces(
                hovertemplate=f"<b>{territory_label.capitalize()}:</b> %{{customdata[0]}}<br>" +
                             "<b>Hospitalisations:</b> %{{customdata[1]:,.0f}}<br><extra></extra>",
                marker_color=MAIN_COLOR
            )
            fig.update_layout(height=600, template='plotly_white')
            col_chart, col_help = st.columns([1, 0.01])
            with col_chart:
                st.plotly_chart(fig, use_container_width=True)
            with col_help:
                st.metric(label="help", value="", help=f"Ce graphique montre le nombre total d'hospitalisations par {territory_label}. Les barres sont triées par ordre croissant.")
        
        with col2:
            # Regrouper les données par territoire et calculer les proportions
            rapport_by_territory = df_nbr_hospi_filtered.groupby(territory_col)[['hospi_total_24h', 'hospi_total_jj', 'total_hospi']].sum().reset_index()
            rapport_by_territory['percent_hospi_total_24h'] = 100 * rapport_by_territory['hospi_total_24h'] / rapport_by_territory['total_hospi']
            rapport_by_territory['percent_hospi_total_jj'] = 100 * rapport_by_territory['hospi_total_jj'] / rapport_by_territory['total_hospi']
            rapport_by_territory = rapport_by_territory.sort_values(by='total_hospi', ascending=True)
            
            # Création du graphique empilé
            fig2 = go.Figure()

            # Ajout des barres pour le nombre d'hospitalisations
            fig2.add_trace(go.Bar(
                x=rapport_by_territory['percent_hospi_total_24h'],
                y=rapport_by_territory[territory_col],
                name='-24h',
                orientation='h',
                marker=dict(color=SECONDARY_COLOR),
                hovertemplate="<b>%{y}:</b> %{x:.1f}%<extra></extra>"
            ))

            fig2.add_trace(go.Bar(
                x=rapport_by_territory['percent_hospi_total_jj'],
                y=rapport_by_territory[territory_col],
                name='+24h',
                orientation='h',
                marker=dict(color=ACCENT_COLOR),
                hovertemplate="<b>%{y}:</b> %{x:.1f}%<extra></extra>"
            ))

            # Mise à jour du layout
            fig2.update_layout(
                barmode='stack',
                title=f'Proportion des types de durée des hospitalisations par {territory_label}',
                xaxis=dict(title='Proportion (%)'),
                yaxis=dict(title=territory_label.capitalize()),
                template='plotly_white',
                height=600
            )
            
            # Affichage du graphique
            st.plotly_chart(fig2, use_container_width=True)

    # Pathologies
    with tab3:
        
        # Système de sélection de pathologie
        all_pathologies = sorted(df_nbr_hospi_filtered['nom_pathologie'].unique())
        all_pathologies.insert(0, "Toutes les pathologies")  # Ajout de l'option pour toutes les pathologies
        selected_pathology = st.selectbox(
            "🔍 Sélectionner une pathologie en médecine pour obtenir des détails",
            all_pathologies,
            key="pathology_selector_med"
        )
        
        # Afficher les données pour la pathologie sélectionnée
        if selected_pathology == "Toutes les pathologies":
            path_data = df_nbr_hospi_filtered[
                (df_nbr_hospi_filtered['niveau'] == niveau_administratif) &
                (df_nbr_hospi_filtered['sexe'] == selected_sex)
            ]
        else:
            path_data = df_nbr_hospi_filtered[
                (df_nbr_hospi_filtered['nom_pathologie'] == selected_pathology) &
                (df_nbr_hospi_filtered['niveau'] == niveau_administratif) &
                (df_nbr_hospi_filtered['sexe'] == selected_sex)
            ]
        
        # Calcul des métriques avec les filtres appliqués
        total_hospi = path_data['nbr_hospi'].sum()
        
        # Calcul de la durée moyenne en fonction de la sélection
        if selected_pathology == "Toutes les pathologies":
            avg_duration = df_duree_hospi_filtered[
                (df_duree_hospi_filtered['niveau'] == niveau_administratif) &
                (df_duree_hospi_filtered['sexe'] == selected_sex)
            ]['AVG_duree_hospi'].mean()
        else:
            avg_duration = df_duree_hospi_filtered[
                (df_duree_hospi_filtered['nom_pathologie'] == selected_pathology) &
                (df_duree_hospi_filtered['niveau'] == niveau_administratif) &
                (df_duree_hospi_filtered['sexe'] == selected_sex)
            ]['AVG_duree_hospi'].mean()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total d'hospitalisations", format_number(total_hospi),help="Nombre total d'hospitalisations")
        with col2:
            st.metric("Durée moyenne", f"{avg_duration:.1f} jours",help="Durée moyenne des séjours hospitaliers")
        with col3:
            st.metric("Indice comparatif", f"{path_data['indice_comparatif_tt_age_percent'].mean():.1f}%", help="Indice comparatif moyen en terme de capacité estimée")
        with col4:
            hospi_24h = pd.to_numeric(path_data['hospi_total_24h'], errors='coerce').sum()  # Convert to numeric first and handle any non-numeric values
            st.metric("Total hospitalisations <24h", format_number(hospi_24h),help="Total d'hospitalisations de moins de 24h")
        with col5:
            # Sélectionner toutes les colonnes tranche_age_*
            age_columns = [col for col in path_data.columns if col.startswith('tranche_age_')]
            # Calculer la somme pour chaque tranche d'âge
            age_sums = path_data[age_columns].sum()
            # Trouver la tranche d'âge avec la plus grande valeur
            most_common_age = age_sums.idxmax().replace('tranche_age_', '')
            st.metric("Tranche d'âge majoritaire", most_common_age)
        
        st.divider()        
        # Ajout d'un sélecteur pour filtrer le nombre de pathologies à afficher
        n_pathologies = st.slider("Nombre de pathologies à afficher", 5, 159, 20)
        
        # Top pathologies par nombre d'hospitalisations
        hospi_by_pathology = df_nbr_hospi_filtered.groupby('nom_pathologie')['nbr_hospi'].sum().reset_index()
        hospi_by_pathology = hospi_by_pathology.sort_values(by='nbr_hospi', ascending=False).head(n_pathologies)
        
        # Ajout des données de durée moyenne
        duree_data = df_duree_hospi_filtered.groupby('nom_pathologie')['AVG_duree_hospi'].mean().reset_index()
        hospi_by_pathology = pd.merge(hospi_by_pathology, duree_data, on='nom_pathologie', how='left')

        # Création d'une figure avec deux axes Y
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Ajout des barres pour le nombre d'hospitalisations
        fig.add_trace(
            go.Bar(
                x=hospi_by_pathology['nom_pathologie'],
                y=hospi_by_pathology['nbr_hospi'],
                name="Nombre d'hospitalisations",
                yaxis='y',
                marker_color=MAIN_COLOR,
                customdata=hospi_by_pathology[['nom_pathologie', 'nbr_hospi']],
                hovertemplate="<b>Pathologie:</b> %{customdata[0]}<br>" +
                            "<b>Hospitalisations:</b> %{customdata[1]:,.0f}<br><extra></extra>"
            ),
            secondary_y=False
        )

        # Ajout de la ligne pour la durée moyenne
        fig.add_trace(
            go.Scatter(
                x=hospi_by_pathology['nom_pathologie'],
                y=hospi_by_pathology['AVG_duree_hospi'],
                name="Durée moyenne de séjour",
                line=dict(color=SECONDARY_COLOR, width=2),
                mode='lines+markers',
                marker=dict(size=6),
                customdata=hospi_by_pathology[['nom_pathologie', 'AVG_duree_hospi']],
                hovertemplate="<b>Pathologie:</b> %{customdata[0]}<br>" +
                            "<b>Durée moyenne:</b> %{customdata[1]:.1f} jours<br><extra></extra>"
            ),
            secondary_y=True
        )

        # Mise à jour de la mise en page
        fig.update_layout(
            title=dict(
                text='Relation entre nombre d\'hospitalisations et durée moyenne de séjour',
                y=0.95,
                x=0.5,
                xanchor='center',
                yanchor='top'
            ),
            height=500,
            template='plotly_white',
            showlegend=False,
            margin=dict(t=100, b=50, l=50, r=50),  # Augmenter la marge du haut pour plus d'espace
        )

        # Mise à jour des titres des axes Y
        fig.update_yaxes(title_text="Nombre d'hospitalisations", secondary_y=False)
        fig.update_yaxes(title_text="Durée moyenne de séjour (jours)", secondary_y=True)

        col_chart, col_help = st.columns([1, 0.01])
        with col_chart:
            st.plotly_chart(fig, use_container_width=True)
        with col_help:
            st.metric(label="help", value="", help="Ce graphique montre la relation entre le nombre d'hospitalisations (barres) et la durée moyenne de séjour (ligne) pour les pathologies les plus fréquentes.")

        # Graphique combiné (scatter plot)
        # Fusion des données d'hospitalisation et de durée par année
        combined_data = pd.merge(
            df_nbr_hospi.groupby(['nom_pathologie', 'year'])['nbr_hospi'].sum().reset_index(),
            df_duree_hospi.groupby(['nom_pathologie', 'year'])['AVG_duree_hospi'].mean().reset_index(),
            on=['nom_pathologie', 'year']
        )
        
        # Filtrer pour garder seulement les n_pathologies plus fréquentes par année
        top_pathologies = df_nbr_hospi_filtered.groupby('nom_pathologie')['nbr_hospi'].sum().nlargest(n_pathologies).index
        combined_data = combined_data[combined_data['nom_pathologie'].isin(top_pathologies)]

        # Normalisation des valeurs pour la taille des points
        max_hospi = combined_data['nbr_hospi'].max()
        combined_data['size'] = (combined_data['nbr_hospi'] / max_hospi * 100).round().astype(int)
        # Création du scatter plot avec animation
        fig = px.scatter(
            combined_data,
            x='nbr_hospi',
            y='AVG_duree_hospi',
            text='nom_pathologie',
            animation_frame=combined_data['year'].dt.year,
            animation_group='nom_pathologie',
            title=f'Relation entre nombre d\'hospitalisations et durée moyenne de séjour',
            labels={'nbr_hospi': 'Nombre d\'hospitalisations',
                   'AVG_duree_hospi': 'Durée moyenne de séjour (jours)',
                   'nom_pathologie': 'Pathologie'},
            size='size',
            size_max=40,
            color='AVG_duree_hospi',
            color_continuous_scale='Viridis',
            range_x=[0.1, combined_data['nbr_hospi'].max() * 1.1],  # Commencer à 0 pour l'axe des hospitalisations
            range_y=[0.5, combined_data['AVG_duree_hospi'].max() * 1.1]  # Commencer à 0 pour la durée moyenne
        )

        # Personnalisation du graphique
        fig.update_traces(
            textposition='top center',
            hovertemplate="<b>%{text}</b><br>" +
                         "Hospitalisations: %{x:,.0f}<br>" +
                         "Durée moyenne: %{y:.1f} jours<br>" +
                         "<extra></extra>"
        )

        # Mise à jour de la mise en page
        fig.update_layout(
            height=800,
            template='plotly_white',
            showlegend=False,
            margin=dict(t=100, b=100, l=100, r=150),
            annotations=[
                dict(
                    text="<b>Légende</b> : <br>La taille des points représente le nombre d'hospitalisations<br>La couleur indique la durée moyenne de séjour",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.8, y=1.1,
                    align="left",
                    xanchor="left"
                )
            ]
        )

        # Configuration de l'animation
        fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1500
        fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 500
        
        col_chart, col_help = st.columns([1, 0.01])
        with col_chart:
            st.plotly_chart(fig, use_container_width=True)
        with col_help:
            st.metric(label="help", value="", help="Ce graphique animé montre l'évolution de la relation entre le nombre d'hospitalisations et la durée moyenne de séjour pour chaque pathologie au fil des années. La taille des bulles représente le nombre d'hospitalisations.")

        # Graphique 3D
        # Fusion des données avec les trois métriques
        combined_data_3d = pd.merge(
            df_nbr_hospi.groupby(['nom_pathologie', 'year'])['nbr_hospi'].sum().reset_index(),
            df_duree_hospi.groupby(['nom_pathologie', 'year'])['AVG_duree_hospi'].mean().reset_index(),
            on=['nom_pathologie', 'year']
        )
        combined_data_3d = pd.merge(
            combined_data_3d,
            df_tranche_age_hospi.groupby(['nom_pathologie', 'year'])['indice_comparatif_tt_age_percent'].mean().reset_index(),
            on=['nom_pathologie', 'year']
        )

        # Filtrer pour garder seulement les n_pathologies plus fréquentes
        top_pathologies = df_nbr_hospi_filtered.groupby('nom_pathologie')['nbr_hospi'].sum().nlargest(n_pathologies).index
        combined_data_3d = combined_data_3d[combined_data_3d['nom_pathologie'].isin(top_pathologies)]

        # Création du graphique 3D avec animation
        fig = go.Figure()

        # Créer les frames pour l'animation avec interpolation
        frames = []
        years = sorted(combined_data_3d['year'].dt.year.unique())
        
        for i in range(len(years)):
            current_year = years[i]
            current_data = combined_data_3d[combined_data_3d['year'].dt.year == current_year].copy()
            
            # Nettoyer les valeurs NA
            current_data = current_data.dropna(subset=['nbr_hospi', 'AVG_duree_hospi', 'indice_comparatif_tt_age_percent'])
            
            # Ajouter la frame pour l'année actuelle
            frame = go.Frame(
                data=[go.Scatter3d(
                    x=current_data['nbr_hospi'].tolist(),
                    y=current_data['AVG_duree_hospi'].tolist(),
                    z=current_data['indice_comparatif_tt_age_percent'].tolist(),
                    mode='markers+text',
                    text=current_data['nom_pathologie'].tolist(),
                    textposition='top center',
                    marker=dict(
                        size=[x/current_data['nbr_hospi'].max()*30 for x in current_data['nbr_hospi']],
                        color=current_data['AVG_duree_hospi'].tolist(),
                        colorscale='Viridis',
                        opacity=0.8,
                        colorbar=dict(title="Durée moyenne de séjour (jours)")
                    ),
                    hovertemplate="<b>%{text}</b><br>" +
                                 f"Année: {current_year}<br>" +
                                 "Hospitalisations: %{x:,.0f}<br>" +
                                 "Durée moyenne: %{y:.1f} jours<br>" +
                                 "Indice comparatif: %{z:.1f}%<br>" +
                                 "<extra></extra>"
                )],
                name=str(current_year)
            )
            frames.append(frame)
            
            # Créer des frames intermédiaires si ce n'est pas la dernière année
            if i < len(years) - 1:
                next_year = years[i + 1]
                next_data = combined_data_3d[combined_data_3d['year'].dt.year == next_year].copy()
                next_data = next_data.dropna(subset=['nbr_hospi', 'AVG_duree_hospi', 'indice_comparatif_tt_age_percent'])
                
                # S'assurer que les données sont alignées
                common_pathologies = sorted(list(set(current_data['nom_pathologie']) & set(next_data['nom_pathologie'])))
                current_data = current_data[current_data['nom_pathologie'].isin(common_pathologies)].sort_values('nom_pathologie')
                next_data = next_data[next_data['nom_pathologie'].isin(common_pathologies)].sort_values('nom_pathologie')
                
                # Créer 5 frames intermédiaires entre chaque année
                for step in range(1, 6):
                    # Interpolation linéaire entre les années
                    alpha = step / 6.0
                    
                    # Calculer les valeurs interpolées
                    nbr_hospi = (current_data['nbr_hospi'].values * (1-alpha) + next_data['nbr_hospi'].values * alpha).tolist()
                    avg_duree = (current_data['AVG_duree_hospi'].values * (1-alpha) + next_data['AVG_duree_hospi'].values * alpha).tolist()
                    indice = (current_data['indice_comparatif_tt_age_percent'].values * (1-alpha) + next_data['indice_comparatif_tt_age_percent'].values * alpha).tolist()
                    
                    # Calculer la taille des points
                    max_hospi = max(nbr_hospi) if nbr_hospi else 1  # Éviter la division par zéro
                    point_sizes = [x/max_hospi*30 for x in nbr_hospi]
                    
                    frame = go.Frame(
                        data=[go.Scatter3d(
                            x=nbr_hospi,
                            y=avg_duree,
                            z=indice,
                            mode='markers+text',
                            text=current_data['nom_pathologie'].tolist(),
                            textposition='top center',
                            marker=dict(
                                size=point_sizes,
                                color=avg_duree,
                                colorscale='Viridis',
                                opacity=0.8,
                                colorbar=dict(title="Durée moyenne de séjour (jours)")
                            ),
                            hovertemplate="<b>%{text}</b><br>" +
                                         f"Transition {current_year}-{next_year}<br>" +
                                         "Hospitalisations: %{x:,.0f}<br>" +
                                         "Durée moyenne: %{y:.1f} jours<br>" +
                                         "Indice comparatif: %{z:.1f}%<br>" +
                                         "<extra></extra>"
                        )],
                        name=f"{current_year}_{step}"
                    )
                    frames.append(frame)
            
            # Ajouter la première année comme trace initiale
            if current_year == years[0]:
                fig.add_trace(frame.data[0])

        fig.frames = frames

        # Mise à jour des steps pour inclure uniquement les années principales
        steps = []
        for year in years:
            step = dict(
                method="animate",
                args=[[str(year)], {
                    "frame": {"duration": 300, "redraw": True},
                    "mode": "immediate",
                    "transition": {"duration": 300}
                }],
                label=str(year)
            )
            steps.append(step)

        sliders = [dict(
            active=0,
            currentvalue={"prefix": "Année: "},
            pad={"t": 50},
            steps=steps
        )]
        
        # Mise en page du graphique 3D
        fig.update_layout(
            title=dict(
                text='Évolution des pathologies selon trois dimensions clés',
                y=0.95,
                x=0.4,
                xanchor='right',
                yanchor='top'
            ),
            scene=dict(
                xaxis_title='Nombre d\'hospitalisations',
                yaxis_title='Durée moyenne de séjour (jours)',
                zaxis_title='Indice comparatif (%)',
                camera=dict(
                    up=dict(x=0, y=0, z=1),
                    center=dict(x=0, y=0, z=0),
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            ),
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99
            ),
            width=800,
            height=600,
            template='plotly_white',
            sliders=sliders,
            annotations=[
                dict(
                    text="<b>Légende</b> : <br>La taille des points représente le nombre d'hospitalisations<br>La couleur indique la durée moyenne de séjour",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.8, y=1.1,
                    align="left",
                    xanchor="left"
                )
            ],
            margin=dict(t=100, b=50, l=50, r=50)  # Augmenter la marge du haut pour plus d'espace
        )

        # Ajout de configuration pour une animation plus fluide
        fig.update_traces(
            hoverinfo="none",  # Désactiver temporairement le hover pendant l'animation
            customdata=combined_data_3d[['nom_pathologie', 'nbr_hospi', 'AVG_duree_hospi', 'indice_comparatif_tt_age_percent']].values,
        )
        
        # Ajout des boutons de contrôle pour l'animation
        fig.update_layout(
            updatemenus=[{
                "buttons": [
                    {
                        "args": [None, {
                            "frame": {"duration": 300, "redraw": True},
                            "fromcurrent": True,
                            "transition": {"duration": 300},
                            "mode": "immediate"
                        }],
                        "label": "Lecture",
                        "method": "animate"
                    },
                    {
                        "args": [[None], {
                            "frame": {"duration": 0, "redraw": True},
                            "mode": "immediate",
                            "transition": {"duration": 0}
                        }],
                        "label": "Pause",
                        "method": "animate"
                    }
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 87},
                "showactive": False,
                "type": "buttons",
                "x": 0.0,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top"
            }]
        )

        # Affichage du graphique
        col_chart, col_help = st.columns([1, 0.01])
        with col_chart:
            st.plotly_chart(fig, use_container_width=True)
        with col_help:
            st.metric(label="help", value="", help="Ce graphique 3D montre la distribution des hospitalisations par pathologie, durée moyenne de séjour et indice comparatif. Utilisez les contrôles pour faire pivoter et zoomer sur le graphique.")

        # Tableau récapitulatif détaillé
        st.subheader("Évolution des pathologies - Augmentation les plus importantes (2018-2022)")
        
        # Calculer les évolutions année par année
        evolutions_by_year = {}
        years = sorted(df_filtered['annee'].unique())
        
        for i in range(len(years)-1):
            current_year = years[i]
            next_year = years[i+1]
            
            # Données pour l'année courante et suivante
            current_data = df_filtered[df_filtered['annee'] == current_year].groupby('nom_pathologie')['nbr_hospi'].sum()
            next_data = df_filtered[df_filtered['annee'] == next_year].groupby('nom_pathologie')['nbr_hospi'].sum()
            
            # Calculer l'évolution en pourcentage
            evolution = ((next_data - current_data) / current_data * 100).fillna(0)
            evolutions_by_year[f'{current_year}-{next_year}'] = evolution
            
        # Créer le DataFrame de base avec le nombre total d'hospitalisations
        df_summary = df_filtered.groupby('nom_pathologie')['nbr_hospi'].sum().reset_index()
        
        # Ajouter les évolutions année par année
        for period, evolution in evolutions_by_year.items():
            df_summary = df_summary.merge(
                evolution.reset_index().rename(columns={'nbr_hospi': f'Evolution_{period}'}),
                on='nom_pathologie',
                how='left'
            )
        
        # Calculer l'évolution globale (2018-2022)
        hospi_2018 = df_filtered[df_filtered['annee'] == min(years)].groupby('nom_pathologie')['nbr_hospi'].sum()
        hospi_2022 = df_filtered[df_filtered['annee'] == max(years)].groupby('nom_pathologie')['nbr_hospi'].sum()
        evolution_globale = ((hospi_2022 - hospi_2018) / hospi_2018 * 100).fillna(0)
        
        # Ajouter l'évolution globale au DataFrame
        df_summary = df_summary.merge(
            evolution_globale.reset_index().rename(columns={'nbr_hospi': 'Evolution_globale'}),
            on='nom_pathologie',
            how='left'
        )
        
        # Trier par évolution globale décroissante
        df_summary = df_summary.sort_values('Evolution_globale', ascending=False)
        
        # Renommer les colonnes pour l'affichage
        df_summary.columns = ['Pathologie', 'Hospitalisations'] + [f'Évol. {period} (%)' for period in evolutions_by_year.keys()] + ['Évol. globale (%)']
        
        # Colonnes d'évolution pour le gradient
        evolution_columns = [col for col in df_summary.columns if 'Évol.' in col]

        # Filtrer les NaN avant de calculer min et max
        evolution_values = df_summary[evolution_columns].values.flatten()
        evolution_values = evolution_values[~pd.isna(evolution_values)]  # Supprime les NaN
        vmin, vmax = evolution_values.min(), evolution_values.max()

        # Formater et afficher le tableau
        st.dataframe(
            df_summary.style.format({
                'Hospitalisations': '{:,.0f}',
                **{col: '{:+.1f}%' for col in evolution_columns}
            }).background_gradient(
                cmap='RdYlGn_r',
                subset=evolution_columns,
                vmin=vmin,
                vmax=vmax
            ),
            use_container_width=True
        )
        
        st.markdown("---")
        
        # Deuxième tableau avec les baisses en premier
        st.subheader("Évolution des pathologies - Baisses les plus importantes (2018-2022)")
        
        # Utiliser le même DataFrame mais trié dans l'ordre inverse
        df_summary_desc = df_summary.sort_values('Évol. globale (%)', ascending=True)
        
        # Filtrer les NaN avant de calculer min et max
        evolution_values_desc = df_summary_desc[evolution_columns].values.flatten()
        evolution_values_desc = evolution_values_desc[~pd.isna(evolution_values_desc)]  # Supprime les NaN
        vmin_desc, vmax_desc = evolution_values_desc.min(), evolution_values_desc.max()

        # Afficher le deuxième tableau
        st.dataframe(
            df_summary_desc.style.format({
                'Hospitalisations': '{:,.0f}',
                **{col: '{:+.1f}%' for col in evolution_columns}
            }).background_gradient(
                cmap='RdYlGn_r',
                subset=evolution_columns,
                vmin=vmin_desc,
                vmax=vmax_desc
            ),
            use_container_width=True
        )        


        
    # Démographie
    with tab4:

        # Taux de recours par tranche d'âge
        age_groups = [
            'tranche_age_0_1', 'tranche_age_1_4', 'tranche_age_5_14',
            'tranche_age_15_24', 'tranche_age_25_34', 'tranche_age_35_44',
            'tranche_age_45_54', 'tranche_age_55_64', 'tranche_age_65_74',
            'tranche_age_75_84', 'tranche_age_85_et_plus'
        ]
        
        age_labels = {
            'tranche_age_0_1': '0-1 an',
            'tranche_age_1_4': '1-4 ans',
            'tranche_age_5_14': '5-14 ans',
            'tranche_age_15_24': '15-24 ans',
            'tranche_age_25_34': '25-34 ans',
            'tranche_age_35_44': '35-44 ans',
            'tranche_age_45_54': '45-54 ans',
            'tranche_age_55_64': '55-64 ans',
            'tranche_age_65_74': '65-74 ans',
            'tranche_age_75_84': '75-84 ans',
            'tranche_age_85_et_plus': '85 ans et plus'
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(" Distribution par tranche d'âge")
            
            # Optimisation du calcul de la moyenne pour les tranches d'âge
            age_means = []
            for col in age_groups:
                mean_value = df_tranche_age_hospi_filtered[col].mean()
                age_means.append({
                    'Tranche d\'âge': age_labels[col],
                    'Taux': mean_value
                })
            
            age_distribution = pd.DataFrame(age_means)
            
            fig = px.bar(age_distribution,
                        x='Tranche d\'âge',
                        y='Taux',
                        title='Distribution des hospitalisations par tranche d\'âge',
                        labels={'Taux': 'Taux d\'hospitalisation'},
                        custom_data=['Tranche d\'âge', 'Taux'])
            
            fig.update_traces(
                hovertemplate="<b>Tranche d'âge:</b> %{customdata[0]}<br>" +
                             "<b>Taux:</b> %{customdata[1]:.2f}%<br><extra></extra>",
                marker_color=MAIN_COLOR
            )
            fig.update_layout(height=500, template='plotly_white')
            col_chart, col_help = st.columns([1, 0.01])
            with col_chart:
                st.plotly_chart(fig, use_container_width=True)
            with col_help:
                st.metric(label="help", value="", help="Ce graphique montre la distribution des hospitalisations par tranche d'âge. Les barres représentent le taux d'hospitalisation pour chaque groupe d'âge.")
        
        with col2:
            st.subheader(" Évolution des taux")
            
            # Calcul de l'évolution des taux standardisés
            evolution_taux = df_tranche_age_hospi_filtered.groupby('year').agg({
                'tx_standard_tt_age_pour_mille': 'mean',
                'tx_brut_tt_age_pour_mille': 'mean'
            }).reset_index()
            
            fig = go.Figure()

            # Ajout des lignes pour les taux standardisés et bruts
            fig.add_trace(go.Scatter(
                x=evolution_taux['year'],
                y=evolution_taux['tx_standard_tt_age_pour_mille'],
                name='Taux standardisé',
                line=dict(color=SECONDARY_COLOR, width=2),
                hovertemplate="<b>Date:</b> %{x|%Y}<br>" +
                             "<b>Taux standardisé:</b> %{y:.2f}‰<br><extra></extra>"
            ))

            fig.add_trace(go.Scatter(
                x=evolution_taux['year'],
                y=evolution_taux['tx_brut_tt_age_pour_mille'],
                name='Taux brut',
                line=dict(color=ACCENT_COLOR, width=2, dash='dash'),
                hovertemplate="<b>Date:</b> %{x|%Y}<br>" +
                             "<b>Taux brut:</b> %{y:.2f}‰<br><extra></extra>"
            ))
            
            fig.update_layout(
                title='Évolution des taux d\'hospitalisation',
                xaxis_title='Année',
                yaxis_title='Taux pour 1000 habitants',
                height=500,
                hovermode='x unified',
                template='plotly_white'
                
            )
            col_chart, col_help = st.columns([1, 0.01])
            with col_chart:
                st.plotly_chart(fig, use_container_width=True)
            with col_help:
                st.metric(label="help", value="", help="Ce graphique montre l'évolution des taux d'hospitalisation au fil du temps. Il permet de comparer les tendances entre différentes régions ou services.")

        # Analyse régionale par tranche d'âge
        st.subheader(" Analyse territoriale par tranche d'âge")
        
        # Sélection du territoire
        territory_col = 'nom_region'
        territories = sorted(df_tranche_age_hospi_filtered[territory_col].unique())
        selected_territory = st.selectbox(
            f"Sélectionner un territoire", 
            territories
        )
        
        # Filtrage des données pour le territoire sélectionné
        territory_data = df_tranche_age_hospi_filtered[df_tranche_age_hospi_filtered[territory_col] == selected_territory]
        territory_age_data = territory_data[age_groups].mean().reset_index()
        territory_age_data.columns = ['Tranche d\'âge', 'Taux']
        territory_age_data['Tranche d\'âge'] = territory_age_data['Tranche d\'âge'].map(age_labels)
        
        fig = px.bar(territory_age_data,
                    x='Tranche d\'âge',
                    y='Taux',
                    title=f'Distribution par tranche d\'âge - {selected_territory}',
                    labels={'Taux': 'Taux d\'hospitalisation'},
                    custom_data=['Tranche d\'âge', 'Taux'])
        
        fig.update_traces(
            hovertemplate="<b>Tranche d'âge:</b> %{customdata[0]}<br>" +
                         "<b>Taux:</b> %{customdata[1]:.2f}%<br><extra></extra>",
            marker_color=MAIN_COLOR
        )
        fig.update_layout(height=500, template='plotly_white')
        col_chart, col_help = st.columns([1, 0.01])
        with col_chart:
            st.plotly_chart(fig, use_container_width=True)
        with col_help:
            st.metric(label="help", value="", help="Ce graphique montre la distribution des hospitalisations par tranche d'âge pour le territoire sélectionné.")


        # Graphique simplifié de la distribution par âge
        
        # Calcul des moyennes par groupe d'âge
        age_means = {
            '0 à 3 ans': df_tranche_age_hospi_filtered[['tranche_age_0_1', 'tranche_age_1_4']].mean(axis=1).mean(),
            '4 à 17 ans': df_tranche_age_hospi_filtered[['tranche_age_5_14', 'tranche_age_15_24']].mean(axis=1).mean(),
            '18 à 59 ans': df_tranche_age_hospi_filtered[['tranche_age_25_34', 'tranche_age_35_44', 'tranche_age_45_54', 'tranche_age_55_64']].mean(axis=1).mean(),
            '60 à 69 ans': df_tranche_age_hospi_filtered['tranche_age_65_74'].mean(),
            '70 à 79 ans': df_tranche_age_hospi_filtered['tranche_age_75_84'].mean(),
            '80 ans et plus': df_tranche_age_hospi_filtered['tranche_age_85_et_plus'].mean()
        }
        
        # Conversion en pourcentages
        total = sum(age_means.values())
        age_percentages = {k: (v/total)*100 for k, v in age_means.items()}
        
        # Création du DataFrame pour le graphique
        df_simplified = pd.DataFrame({
            'Tranche d\'âge': list(age_percentages.keys()),
            'Pourcentage': list(age_percentages.values())
        })
        
        
    @st.cache_data
    def prepare_hospi_data():
        hospi_columns = ['year', 'region', 'nom_region', 'pathologie', 'nom_pathologie', 'nbr_hospi']
        df_hospi = df_nbr_hospi[hospi_columns].copy()
        df_hospi['year'] = pd.to_datetime(df_hospi['year']).dt.date
        df_hospi['nbr_hospi'] = df_hospi['nbr_hospi'].astype('float32')
        return df_hospi

    @st.cache_data
    def prepare_duree_data():
        duree_columns = ['year', 'region', 'nom_region', 'pathologie', 'nom_pathologie', 'sexe', 'AVG_duree_hospi']
        df_duree = df_duree_hospi[duree_columns].copy()
        df_duree['year'] = pd.to_datetime(df_duree['year']).dt.date
        df_duree['AVG_duree_hospi'] = df_duree['AVG_duree_hospi'].astype('float32')
        return df_duree

    @st.cache_data
    def prepare_age_data():
        age_columns = ['year', 'region', 'nom_region', 'pathologie', 'nom_pathologie', 
                      'tx_brut_tt_age_pour_mille', 'tx_standard_tt_age_pour_mille']
        df_age = df_tranche_age_hospi[age_columns].copy()
        df_age['year'] = pd.to_datetime(df_age['year']).dt.date
        df_age['tx_brut_tt_age_pour_mille'] = df_age['tx_brut_tt_age_pour_mille'].astype('float32')
        df_age['tx_standard_tt_age_pour_mille'] = df_age['tx_standard_tt_age_pour_mille'].astype('float32')
        return df_age
        
    # Création d'un nouvel onglet pour l'analyse par service médical
    with tab5:
        
        # Filtrer les données pour n'avoir que les totaux par service
        df_service = df_complet[df_complet['sexe'] == 'Ensemble'].copy()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Sélection de l'année
            selected_year = st.selectbox(
                "Sélectionner l'année",
                sorted(df_service['annee'].unique()),
                key='service_year'
            )
        
        with col2:
            # Sélection de la région
            selected_region = st.selectbox(
                "Sélectionner la région",
                ['France entière'] + sorted(df_service['nom_region'].unique()),
                key='service_region'
            )
        
        # Filtrer les données selon les sélections
        mask = (df_service['annee'] == selected_year)
        if selected_region != 'France entière':
            mask &= (df_service['nom_region'] == selected_region)
        
        df_service_filtered = df_service[mask]
        
        # Création des groupes d'âge
        df_service_filtered['age_enfants'] = df_service_filtered[['tranche_age_0_1', 'tranche_age_1_4', 
            'tranche_age_5_14']].sum(axis=1)
        df_service_filtered['age_jeunes'] = df_service_filtered['tranche_age_15_24']
        df_service_filtered['age_adultes'] = df_service_filtered[['tranche_age_25_34', 
            'tranche_age_35_44']].sum(axis=1)
        df_service_filtered['age_seniors'] = df_service_filtered[['tranche_age_45_54', 
            'tranche_age_55_64']].sum(axis=1)
        df_service_filtered['age_ages'] = df_service_filtered[['tranche_age_65_74', 'tranche_age_75_84', 
            'tranche_age_85_et_plus']].sum(axis=1)

        age_columns = [col for col in df_service.columns if col.startswith('tranche_age_')]
        
        df_age_service = df_service_filtered.groupby('classification')[age_columns].mean().reset_index()
        df_age_service_melted = pd.melt(
            df_age_service,
            id_vars=['classification'],
            value_vars=age_columns,
            var_name='tranche_age',
            value_name='pourcentage'
        )
        
        # Nettoyer les noms des tranches d'âge
        df_age_service_melted['tranche_age'] = df_age_service_melted['tranche_age'].str.replace('tranche_age_', '')
        
        fig_heatmap = px.density_heatmap(
            df_age_service_melted,
            x='tranche_age',
            y='classification',
            z='pourcentage',
            title='Distribution des tranches d\'âge par service médical',
            labels={'tranche_age': 'Tranche d\'âge', 'classification': 'Service', 'pourcentage': 'Pourcentage'},
            color_continuous_scale='redor'
        )
        fig_heatmap.update_layout(xaxis_tickangle=-45, template='plotly_white')
        col_chart, col_help = st.columns([1, 0.01])
        with col_chart:
            st.plotly_chart(fig_heatmap, use_container_width=True)
        with col_help:
            st.metric(label="help", value="", help="Cette heatmap montre la distribution des tranches d'âge pour chaque service médical. Les couleurs plus foncées indiquent une plus forte concentration.")

        # Création du dataframe pour les tranches d'âge regroupées
        age_groups = ['Enfants (0-14)', 'Jeunes (15-24)', 'Adultes (25-44)', 'Seniors (45-64)', 'Personnes âgées (65+)']
        df_age_grouped = df_service_filtered.groupby('classification').agg({
            'age_enfants': 'mean',
            'age_jeunes': 'mean',
            'age_adultes': 'mean',
            'age_seniors': 'mean',
            'age_ages': 'mean',
            'nbr_hospi': 'sum'
        }).reset_index()
        
        # Pie chart interactif
        fig_pie = px.pie(
            df_service_filtered.groupby('classification')['nbr_hospi'].sum().reset_index(),
            values='nbr_hospi',
            names='classification',
            title=f'Répartition des hospitalisations par service médical ({selected_year})',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(template='plotly_white')
        col_chart, col_help = st.columns([1, 0.01])
        with col_chart:
            st.plotly_chart(fig_pie, use_container_width=True)
        with col_help:
            st.metric(label="help", value="", help=f"Ce graphique circulaire montre la répartition des hospitalisations entre les différents services médicaux pour l'année {selected_year}.")

        # Évolution temporelle par service
        df_evolution = df_service.groupby(['annee', 'classification'])['nbr_hospi'].sum().reset_index()
        
        fig_evolution = px.line(
            df_evolution,
            x='annee',
            y='nbr_hospi',
            color='classification',
            title='Évolution des hospitalisations par service médical',
            labels={'annee': 'Année', 'nbr_hospi': 'Nombre d\'hospitalisations', 'classification': 'Service'}
        )
        fig_evolution.update_layout(template='plotly_white')
        col_chart, col_help = st.columns([1, 0.01])
        with col_chart:
            st.plotly_chart(fig_evolution, use_container_width=True)
        with col_help:
            st.metric(label="help", value="", help="Ce graphique montre l'évolution du nombre d'hospitalisations pour chaque service médical au fil du temps.")


st.markdown("---")
st.markdown("Développé avec 💫| Le Wagon - Batch #1834 - Promotion 2024")
