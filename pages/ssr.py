import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from google.cloud import bigquery

# Définition des couleurs du thème
MAIN_COLOR = '#003366'  # Bleu marine principal
SECONDARY_COLOR = '#AFDC8F'  # Vert clair complémentaire
ACCENT_COLOR = '#3D7317'  # Vert foncé pour les accents

# Style CSS personnalisé
st.markdown("""
    <style>
    .main-title {
        color: #003366;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
        text-align: center;
    }
    .section-title {
        color: #003366;
        font-size: 1.8rem;
        font-weight: bold;
        margin: 1.5rem 0;
    }
    .card {
        padding: 1rem;
        border-radius: 10px;
        background-color: #f8f9fa;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Titre principal
st.markdown("<h1 class='main-title' style='margin-top: -70px;'>♿ Service SSR (Soins de santé et de réhabilitation)</h1>", unsafe_allow_html=True)


# Fonction de chargement des données
@st.cache_resource
def load_data():
    try:
        # Chargement des secrets
        gcp_service_account = st.secrets["gcp_service_account"]
        client = bigquery.Client.from_service_account_info(gcp_service_account)
        
        # Requête SQL pour les données SSR
        
        df = client.query("""
            SELECT *
            FROM `projet-jbn-data-le-wagon.dbt_medical_analysis_join_total_morbidite.class_join_total_morbidite_sexe_population`
            WHERE classification = 'SSR' AND niveau = 'Départements'
        """).to_dataframe()

        return df
        
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {str(e)}")
        return None

# Chargement des données
df = load_data()

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

if df is not None:
    # Récupérer les paramètres de l'URL si présents
    params = st.query_params
    
    # Récupération des valeurs uniques pour les filtres
    sexe_options = ["Ensemble", "Femme", "Homme"]
    years = sorted(df['annee'].unique(), reverse=True)
    years_options = ["Toutes les années"] + [str(year) for year in years]
    regions = sorted(df['nom_region'].unique())
    regions_options = ["Tous les départements"] + regions
    
    # Récupération des paramètres avec validation
    default_sexe = params.get('sexe', 'Ensemble')
    if default_sexe not in sexe_options:
        default_sexe = 'Ensemble'
        
    default_annee = params.get('annee', 'Toutes les années')
    if default_annee not in years_options:
        default_annee = 'Toutes les années'
    
    # Gestion du département sélectionné
    default_departement = params.get('departement')
    if default_departement:
        # Si un département est spécifié, on le cherche dans les données
        if default_departement in regions:
            default_region = default_departement
        else:
            default_region = 'Tous les départements'
    else:
        default_region = params.get('region', 'Tous les départements')
        if default_region not in regions_options:
            default_region = 'Tous les départements'

    # Liste déroulante de toutes les pathologies
    all_pathologies = sorted(df['nom_pathologie'].unique())
    all_pathologies.insert(0, "Toutes les pathologies")
    
    # Récupération du paramètre pathologie avec validation
    default_pathologie = params.get('pathologie', 'Toutes les pathologies')
    if default_pathologie not in all_pathologies:
        default_pathologie = 'Toutes les pathologies'
    
    # Filtres principaux en colonnes
    col1, col2, col3 = st.columns(3)

    with col1:
        # Sélection du sexe
        selected_sexe = st.selectbox(
            "Sexe",
            sexe_options,
            key="selecteur_sexe_ssr",
            index=sexe_options.index(default_sexe)
        )

    with col2:
        # Filtre année
        selected_year = st.selectbox(
            "Année", 
            years_options, 
            key="year_filter_ssr",
            index=years_options.index(default_annee)
        )
        
    with col3:
        # Sélection du département
        selected_region = st.selectbox(
            "Départements",
            regions_options,
            key="region_filter_ssr",
            index=regions_options.index(default_region)
        )
    
    selected_pathology = st.selectbox(
        "🔍 Sélectionner une pathologie en SSR pour obtenir des détails",
        all_pathologies,
        key="pathology_selector_ssr",
        index=all_pathologies.index(default_pathologie)
    )
    
    # Mettre à jour les paramètres de l'URL
    st.query_params['sexe'] = selected_sexe
    st.query_params['annee'] = selected_year
    st.query_params['departement'] = selected_region if selected_region != "Tous les départements" else None
    st.query_params['pathologie'] = selected_pathology if selected_pathology != "Toutes les pathologies" else None

    # Filtrage des données selon les sélections
    df_filtered = df.copy()
    
    # Filtre par sexe
    if selected_sexe != "Ensemble":
        df_filtered = df_filtered[df_filtered['sexe'] == selected_sexe]
        
    # Filtre par année
    if selected_year != "Toutes les années":
        df_filtered = df_filtered[df_filtered['annee'] == int(selected_year)]
        
    # Filtre par départements
    if selected_region != "Tous les départements":
        df_filtered = df_filtered[df_filtered['nom_region'] == selected_region]
        
    # Afficher les données pour la pathologie sélectionnée
    if selected_pathology == "Toutes les pathologies":
        path_data = df_filtered[
            (df_filtered['sexe'] == selected_sexe)
        ]
    else:
        path_data = df_filtered[
            (df_filtered['nom_pathologie'] == selected_pathology) &
            (df_filtered['sexe'] == selected_sexe)
        ]
    
    # Calcul des métriques avec les filtres appliqués
    total_hospi = path_data['nbr_hospi'].sum()
    
    # Calcul de la durée moyenne en fonction de la sélection
    if selected_pathology == "Toutes les pathologies":
        avg_duration = df_filtered[
            (df_filtered['sexe'] == selected_sexe)
        ]['AVG_duree_hospi'].mean()
    else:
        avg_duration = df_filtered[
            (df_filtered['nom_pathologie'] == selected_pathology) &
            (df_filtered['sexe'] == selected_sexe)
        ]['AVG_duree_hospi'].mean()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total d'hospitalisations", format_number(total_hospi))
    with col2:
        st.metric("Durée moyenne", f"{avg_duration:.1f} jours")
    with col3:
        st.metric("Indice comparatif", f"{path_data['indice_comparatif_tt_age_percent'].mean():.1f}%")
    with col4:
        hospi_24h = path_data['hospi_total_24h'].sum()
        percentage_24h = (hospi_24h / total_hospi * 100) if total_hospi > 0 else 0
        st.metric("Hospitalisations < 24h", f"{percentage_24h:.1f}%")
    with col5:
        # Sélectionner toutes les colonnes tranche_age_*
        age_columns = [col for col in path_data.columns if col.startswith('tranche_age_')]
        # Calculer la somme pour chaque tranche d'âge
        age_sums = path_data[age_columns].sum()
        # Trouver la tranche d'âge avec la plus grande valeur
        most_common_age = age_sums.idxmax().replace('tranche_age_', '')
        st.metric("Tranche d'âge majoritaire", most_common_age)
    
    tab1, tab2, tab3 = st.tabs([
        "📈 Analyse par pathologies",
        "🗺️ Analyse par capacité",
        "📊 Analyse démographique",
    ])

    with tab1:
        # Ajout d'un sélecteur pour filtrer le nombre de pathologies à afficher
        n_pathologies = st.slider("Nombre de pathologies à afficher", 5, 6, 6)
        
        # Top pathologies par nombre d'hospitalisations
        hospi_by_pathology = df_filtered.groupby('nom_pathologie').agg({
            'nbr_hospi': 'sum',
            'AVG_duree_hospi': 'mean'
        }).reset_index()
        
        hospi_by_pathology = hospi_by_pathology.sort_values(by='nbr_hospi', ascending=False).head(n_pathologies)

        # Création d'une figure avec deux axes Y
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Ajout des barres pour le nombre d'hospitalisations
        fig.add_trace(
            go.Bar(
                x=hospi_by_pathology['nom_pathologie'],
                y=hospi_by_pathology['nbr_hospi'],
                name="Nombre d'hospitalisations",
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
                text='Pathologies SSR : Hospitalisations et durée moyenne de séjour',
                y=0.95,
                x=0.5,
                xanchor='right',
                yanchor='top'
            ),
            height=500,
            template='plotly_white',
            showlegend=False,
            margin=dict(t=100, b=50, l=50, r=50)
        )

        # Mise à jour des titres des axes Y
        fig.update_yaxes(title_text="Nombre d'hospitalisations", secondary_y=False)
        fig.update_yaxes(title_text="Durée moyenne de séjour (jours)", secondary_y=True)

        # Affichage du graphique avec une colonne d'aide
        col_chart, col_help = st.columns([1, 0.01])
        with col_chart:
            st.plotly_chart(fig, use_container_width=True)
        with col_help:
            st.metric(label="help", value="", help="Ce graphique montre la relation entre le nombre d'hospitalisations (barres) et la durée moyenne de séjour (ligne) pour les pathologies SSR les plus fréquentes.")

        # Préparation des DataFrames pour les graphiques
        df_nbr_hospi = df_filtered.copy()
        df_duree_hospi = df_filtered.copy()
        df_tranche_age_hospi = df_filtered.copy()

        st.markdown("---")
        # Graphique combiné (scatter plot)
        # Fusion des données d'hospitalisation et de durée par année
        combined_data = pd.merge(
            df_nbr_hospi.groupby(['nom_pathologie', 'annee'])['nbr_hospi'].sum().reset_index(),
            df_duree_hospi.groupby(['nom_pathologie', 'annee'])['AVG_duree_hospi'].mean().reset_index(),
            on=['nom_pathologie', 'annee']
        )
        
        # Filtrer pour garder seulement les n_pathologies plus fréquentes par année
        top_pathologies = df_nbr_hospi.groupby('nom_pathologie')['nbr_hospi'].sum().nlargest(n_pathologies).index
        combined_data = combined_data[combined_data['nom_pathologie'].isin(top_pathologies)]

        # Calcul des marges pour les axes en prenant en compte les maximums par année
        max_hospi_by_year = combined_data.groupby('annee')['nbr_hospi'].max().max()
        max_duree_by_year = combined_data.groupby('annee')['AVG_duree_hospi'].max().max()
        
        x_margin = max_hospi_by_year * 0.2  # Augmentation de la marge à 20%
        y_margin = max_duree_by_year * 0.2  # Augmentation de la marge à 20%

        # Création du scatter plot avec animation
        if selected_year != "Toutes les années":
            # Si une année spécifique est sélectionnée, créer un scatter plot statique
            fig = px.scatter(
                combined_data,
                x='nbr_hospi',
                y='AVG_duree_hospi',
                text='nom_pathologie',
                title=f'Relation entre nombre d\'hospitalisations et durée moyenne de séjour ({selected_year})',
                labels={'nbr_hospi': 'Nombre d\'hospitalisations',
                    'AVG_duree_hospi': 'Durée moyenne de séjour (jours)',
                    'nom_pathologie': 'Pathologie'},
                size=combined_data['nbr_hospi'].tolist(),
                size_max=40,
                color='AVG_duree_hospi',
                color_continuous_scale='Oryel',
                range_x=[0, max_hospi_by_year + x_margin],
                range_y=[0, max_duree_by_year + y_margin]
            )
        else:
            # Si toutes les années sont sélectionnées, créer le scatter plot animé
            fig = px.scatter(
                combined_data,
                x='nbr_hospi',
                y='AVG_duree_hospi',
                text='nom_pathologie',
                animation_frame='annee',
                animation_group='nom_pathologie',
                title=f'Relation entre nombre d\'hospitalisations et durée moyenne de séjour',
                labels={'nbr_hospi': 'Nombre d\'hospitalisations',
                    'AVG_duree_hospi': 'Durée moyenne de séjour (jours)',
                    'nom_pathologie': 'Pathologie'},
                size=combined_data['nbr_hospi'].tolist(),
                size_max=40,
                color='AVG_duree_hospi',
                color_continuous_scale='Oryel',
                range_x=[0, max_hospi_by_year + x_margin],
                range_y=[0, max_duree_by_year + y_margin]
            )
            
            # Configuration de l'animation
            if hasattr(fig, 'layout') and hasattr(fig.layout, 'updatemenus'):
                try:
                    fig.layout.sliders[0].x = 0.1
                    fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 1500
                    fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 500
                except (IndexError, KeyError, AttributeError):
                    pass  # Ignorer les erreurs si la configuration de l'animation échoue
                    
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

        # Affichage du graphique avec une colonne d'aide
        col_chart, col_help = st.columns([1, 0.01])
        with col_chart:
            st.plotly_chart(fig, use_container_width=True)
        with col_help:
            st.metric(label="help", value="", help="Ce graphique animé montre l'évolution de la relation entre le nombre d'hospitalisations et la durée moyenne de séjour pour chaque pathologie au fil des années. La taille des bulles représente le nombre d'hospitalisations.")
        st.markdown("---")
        # Graphique 3D
        # Fusion des données avec les trois métriques
        combined_data_3d = pd.merge(
            df_nbr_hospi.groupby(['nom_pathologie', 'annee'])['nbr_hospi'].sum().reset_index(),
            df_duree_hospi.groupby(['nom_pathologie', 'annee'])['AVG_duree_hospi'].mean().reset_index(),
            on=['nom_pathologie', 'annee']
        )
        combined_data_3d = pd.merge(
            combined_data_3d,
            df_tranche_age_hospi.groupby(['nom_pathologie', 'annee'])['indice_comparatif_tt_age_percent'].mean().reset_index(),
            on=['nom_pathologie', 'annee']
        )

        # Filtrer pour garder seulement les n_pathologies plus fréquentes
        top_pathologies = df_nbr_hospi.groupby('nom_pathologie')['nbr_hospi'].sum().nlargest(n_pathologies).index
        combined_data_3d = combined_data_3d[combined_data_3d['nom_pathologie'].isin(top_pathologies)]

        # Création du graphique 3D avec animation
        fig = go.Figure()

        # Créer les frames pour l'animation avec interpolation
        frames = []
        years = sorted(combined_data_3d['annee'].unique())
        
        for i in range(len(years)):
            current_year = years[i]
            next_year = years[i+1] if i < len(years) - 1 else None
            
            # Données pour l'année courante
            current_data = combined_data_3d[combined_data_3d['annee'] == current_year].copy()
            
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
                        colorscale='Oryel',
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
            if next_year is not None:
                next_data = combined_data_3d[combined_data_3d['annee'] == next_year].copy()
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
                                colorscale='Oryel',
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
            height=800,
            template='plotly_white',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=1.25,
                xanchor="right",
                x=0.99
            ),
            width=800,
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
            margin=dict(t=100, b=50, l=50, r=50),  # Augmenter la marge du haut pour plus d'espace
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

        # Ajout de configuration pour une animation plus fluide
        fig.update_traces(
            hoverinfo="none",  # Désactiver temporairement le hover pendant l'animation
            customdata=combined_data_3d[['nom_pathologie', 'nbr_hospi', 'AVG_duree_hospi', 'indice_comparatif_tt_age_percent']].values,
        )

        # Affichage du graphique 3D
        col_chart, col_help = st.columns([1, 0.01])
        with col_chart:
            st.plotly_chart(fig, use_container_width=True)
        with col_help:
            st.metric(label="help", value="", help="Ce graphique 3D montre la distribution des hospitalisations par pathologie, durée moyenne de séjour et indice comparatif. Utilisez les contrôles pour faire pivoter et zoomer sur le graphique.")
        st.markdown("---")
        # Tableau récapitulatif détaillé
        st.subheader("Évolution des pathologies (2018-2022)")
        
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
        
    with tab2:
        
        # Requête pour les données de capacité
        @st.cache_resource
        def load_capacity_data():
            try:
                client = bigquery.Client.from_service_account_info(st.secrets["gcp_service_account"])
                df_capacity = client.query("""
                    SELECT *
                    FROM `projet-jbn-data-le-wagon.dbt_medical_analysis_join_total_morbidite_capacite.class_join_total_morbidite_capacite_kpi`
                    WHERE classification = 'SSR' AND niveau = 'Départements'
                """).to_dataframe()
                return df_capacity
            except Exception as e:
                st.error(f"Erreur lors du chargement des données de capacité : {str(e)}")
                return None

        df_capacity = load_capacity_data()

        if df_capacity is not None:
            # Filtrage des données selon l'année sélectionnée
            if selected_year != "Toutes les années":
                df_capacity = df_capacity[df_capacity['annee'] == int(selected_year)]
                
            # Filtrage des données selon le département sélectionné
            if selected_region != "Tous les départements":
                df_capacity = df_capacity[df_capacity['nom_region'] == selected_region]

            # Métriques clés (utilisant df_capacity non filtré par le slider)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_lits = df_capacity['lit_hospi_complete'].sum()
                st.metric("Lits d'hospitalisation", format_number(total_lits))
            with col2:
                total_places = df_capacity['place_hospi_partielle'].sum()
                st.metric("Places en hospitalisation partielle", format_number(total_places))
            with col3:
                taux_occ = df_capacity['taux_occupation'].iloc[0]
                st.metric("Taux d'occupation", f"{taux_occ*100:.1f}%")
            with col4:
                taux_equip = df_capacity['taux_equipement'].iloc[0]
                st.metric("Taux d'équipement", f"{taux_equip} lits pour 1000 Habitants")

            # Calculer le nombre total d'hospitalisations par département
            total_hospi_by_dept = df_capacity.groupby('nom_region').agg({
                'hospi_total_24h': 'sum',
                'hospi_1J': 'sum',
                'hospi_2J': 'sum',
                'hospi_3J': 'sum',
                'hospi_4J': 'sum',
                'hospi_5J': 'sum',
                'hospi_6J': 'sum',
                'hospi_7J': 'sum',
                'hospi_8J': 'sum',
                'hospi_9J': 'sum',
                'hospi_10J_19J': 'sum',
                'hospi_20J_29J': 'sum',
                'hospi_30J': 'sum'
            }).reset_index()
            
            # Calculer le total des hospitalisations
            colonnes_hospi = ['hospi_total_24h', 'hospi_1J', 'hospi_2J', 'hospi_3J', 
                            'hospi_4J', 'hospi_5J', 'hospi_6J', 'hospi_7J', 'hospi_8J', 
                            'hospi_9J', 'hospi_10J_19J', 'hospi_20J_29J', 'hospi_30J']
            
            total_hospi_by_dept['total_hospi'] = total_hospi_by_dept[colonnes_hospi].sum(axis=1)
            
            # Trier les départements par nombre total d'hospitalisations
            total_hospi_by_dept = total_hospi_by_dept.sort_values('total_hospi', ascending=False)
            
            # Slider pour sélectionner le nombre de départements à afficher
            st.markdown("---")

            n_departements = st.slider(
                "Nombre de départements à afficher (triés par nombre d'hospitalisations croissants)",
                min_value=5,
                max_value=len(total_hospi_by_dept),
                value=20
            )
            
            # Créer une copie des données pour les visualisations filtrées par le slider
            df_capacity_filtered = df_capacity.copy()
            
            # Filtrer les départements selon le slider
            top_departements = total_hospi_by_dept['nom_region'].head(n_departements).tolist()
            df_capacity_filtered = df_capacity_filtered[df_capacity_filtered['nom_region'].isin(top_departements)]

            # Pour la suite du code, utiliser df_capacity_filtered au lieu de df_capacity
            # Scatter plot animé avec Plotly Express
            df_scatter = df_capacity_filtered.groupby(['annee', 'nom_region']).agg({
                'taux_occupation': 'first',
                'lit_hospi_complete': 'sum',
                'sejour_hospi_complete': 'sum'
            }).reset_index()
            
            # Multiplier le taux d'occupation par 100
            df_scatter['taux_occupation'] = df_scatter['taux_occupation'] * 100

            # Créer le graphique animé avec Plotly Express
            fig4 = px.scatter(df_scatter, 
                x='lit_hospi_complete',
                y='taux_occupation',
                animation_frame='annee',
                size='sejour_hospi_complete',
                color='sejour_hospi_complete',
                hover_name='nom_region',
                text='nom_region',
                size_max=50,
                color_continuous_scale='Rainbow',
                labels={
                    'value': 'Nombre',
                    'variable': 'Type',
                    'annee': 'Année',
                    'lit_hospi_complete': "Lits d'hospitalisation complète",
                    'sejour_hospi_complete': "Nombre de séjours",
                    'taux_occupation': "Taux d'occupation (%)"
                },
                title="Évolution de la capacité et du taux d'occupation par départements"
            )
            fig4.update_traces(
                hovertemplate="<b>%{hovertext}</b><br>" +
                              "Lits: " + format_number("%{x}") + "<br>" +
                              "Taux d'occupation: %{y:.1f}%<br>" +
                              "Séjours: " + format_number("%{marker.size}")
            )

            # Personnaliser le layout
            fig4.update_traces(
                textposition='top center',
                mode='markers+text'
            )

            # Calculer les limites des axes basées sur les données
            x_margin = (df_scatter['lit_hospi_complete'].max() - df_scatter['lit_hospi_complete'].min()) * 0.1
            y_margin = (df_scatter['taux_occupation'].max() - df_scatter['taux_occupation'].min()) * 0.1

            fig4.update_layout(
                height=600,
                showlegend=False,
                xaxis=dict(
                    range=[
                        df_scatter['lit_hospi_complete'].min() - x_margin,
                        df_scatter['lit_hospi_complete'].max() + x_margin
                    ]
                ),
                yaxis=dict(
                    range=[
                        max(0, df_scatter['taux_occupation'].min() - y_margin),
                        df_scatter['taux_occupation'].max() + y_margin
                    ]
                ),
                updatemenus=[{
                    'type': 'buttons',
                    'showactive': False,
                    'y': -0.1,
                    'x': 0.1,
                    'xanchor': 'right',
                    'yanchor': 'top',
                    'pad': {'t': 0, 'r': 10}
                }],
                sliders=[{
                    'currentvalue': {
                        'font': {'size': 12},
                        'prefix': 'Année: ',
                        'visible': True,
                        'xanchor': 'right'
                    },
                    'pad': {'b': 10, 't': 50},
                    'len': 0.9,
                    'x': 0.1,
                    'y': 0.05,
                }]
            )

            # Formater les axes
            fig4.update_xaxes(
                tickformat=",",
                range=[0, 6000]  # Plage plus large pour l'axe X
            )
            fig4.update_yaxes(
                tickformat=".1f",
                range=[0, 20]  # Maintenir la plage pour le taux d'occupation
            )

            # Affichage du graphique avec une colonne d'aide
            col_chart1, col_help1 = st.columns([1, 0.01])
            with col_chart1:
                st.plotly_chart(fig4, use_container_width=True)
            with col_help1:
                st.metric(
                    label="help",
                    value="",
                    help="Ce graphique animé montre l'évolution de la relation entre la capacité d'accueil (nombre de lits) "
                         "et le taux d'occupation pour chaque départements. La taille et la couleur des bulles représentent "
                         "le nombre de séjours. Utilisez les contrôles d'animation pour voir l'évolution dans le temps."
                )

            # Préparer les données pour le graphique de répartition par durée
            df_duree = df_capacity_filtered.groupby('annee').agg({
                'hospi_total_24h': 'sum',
                'hospi_1J': 'sum',
                'hospi_2J': 'sum',
                'hospi_3J': 'sum',
                'hospi_4J': 'sum',
                'hospi_5J': 'sum',
                'hospi_6J': 'sum',
                'hospi_7J': 'sum',
                'hospi_8J': 'sum',
                'hospi_9J': 'sum',
                'hospi_10J_19J': 'sum',
                'hospi_20J_29J': 'sum',
                'hospi_30J': 'sum',
                'lit_hospi_complete': 'sum',
                'journee_hospi_complete': 'sum',
                'taux_occupation': 'mean'
            }).reset_index()

            # Regrouper les hospitalisations de 1-9 jours
            df_duree['hospi_1J_9J'] = df_duree[[f'hospi_{i}J' for i in range(1, 10)]].sum(axis=1)
            
            # Regrouper les hospitalisations de 20 jours et plus
            df_duree['hospi_20J_plus'] = df_duree['hospi_20J_29J'] + df_duree['hospi_30J']

            # Multiplier le taux d'occupation par 100 pour l'affichage en pourcentage
            df_duree['taux_occupation'] = df_duree['taux_occupation'] * 100

            # Créer le graphique avec Plotly Express
            fig_duree = px.bar(df_duree, 
                x='annee',
                y=['hospi_total_24h', 'hospi_1J_9J', 'hospi_10J_19J', 'hospi_20J_plus'],
                title="Répartition des hospitalisations par durée",
                barmode='stack',
                labels={
                    'value': 'Nombre d\'hospitalisations',
                    'variable': 'Durée',
                    'annee': 'Année',
                    'hospi_total_24h': '24h',
                    'hospi_1J_9J': '1-9 jours',
                    'hospi_10J_19J': '10-19 jours',
                    'hospi_20J_plus': '20 jours et plus'
                },
                color_discrete_map={
                    'hospi_total_24h': '#F5F5DC',
                    'hospi_1J_9J': '#AFDC8F',
                    'hospi_10J_19J': '#3D7317',
                    'hospi_20J_plus': '#003366'
                }
            )

            # Ajouter la ligne de taux d'occupation 
            fig_duree.add_scatter(
                x=df_duree['annee'],
                y=df_duree['taux_occupation'],
                name="Taux d'occupation",
                mode='lines+markers+text',
                text=df_duree['taux_occupation'].apply(lambda x: f"{x:.1f}%"),
                textposition="top center",
                line=dict(color='red', width=2),
                yaxis='y2'
            )

            # Mise à jour du layout
            fig_duree.update_layout(
                yaxis2=dict(
                    title="Taux d'occupation (%)",
                    overlaying='y',
                    side='right',
                    showgrid=False,
                    range=[0, 250],  # Ajuster l'échelle de 0 à 200%
                    tickformat=".0f"
                ),
                height=500,
                legend=dict(
                    orientation="h",  # Légende horizontale
                    yanchor="bottom",
                    y=1.35,  # Position plus haute
                    xanchor="right",
                    x=1,
                    title=dict(text="Durée")  # Ajout d'un titre à la légende
                ),
                margin=dict(t=150, b=100, l=50, r=50)  # Augmentation de la marge supérieure
            )

            # Affichage du graphique avec une colonne d'aide
            col_chart4, col_help4 = st.columns([1, 0.01])
            with col_chart4:
                st.plotly_chart(fig_duree, use_container_width=True)
            with col_help4:
                st.metric(
                    label="help",
                    value="",
                    help="Ce graphique montre la répartition des hospitalisations par durée de séjour. "
                         "Les barres empilées représentent le nombre d'hospitalisations pour chaque durée "
                         "(24h, 1-9 jours, 10-19 jours, 20 jours et plus). "
                         "La ligne rouge indique le taux d'occupation des lits, permettant d'analyser "
                         "la relation entre la durée des séjours et l'utilisation des capacités."
                )

            # Préparer les données pour le graphique de répartition par lits
            df_equip = df_capacity_filtered.groupby('annee').agg({
                'lit_hospi_complete': 'sum',
                'place_hospi_partielle': 'sum',
                'taux_equipement': 'mean'
            }).reset_index()
    
            # Créer le graphique avec Plotly Express
            fig_equip = px.bar(df_equip, 
                x='annee',
                y=['lit_hospi_complete', 'place_hospi_partielle'],
                title="Répartition des lits et places d'hospitalisation disponibles",
                barmode='stack',
                labels={
                    'value': 'Nombre de lits et places',
                    'variable': 'Nombre',
                    'annee': 'Année',
                    'lit_hospi_complete': "1 jour et plus",
                    'place_hospi_partielle': "24 h",
                },
                color_discrete_map={
                    'lit_hospi_complete': '#6fffe9',
                    'place_hospi_partielle': '#5bc0be',
                }
            )

            # Ajouter la ligne de taux d'équipement 
            fig_equip.add_scatter(
                x=df_equip['annee'],
                y=df_equip['taux_equipement'],
                name="Taux d'équipement",
                mode='lines+markers+text',
                text=df_equip['taux_equipement'].apply(lambda x: f"{x:.1f}"),
                textposition="top center",
                line=dict(color='orange', width=2),
                yaxis='y2'
            )

            # Mise à jour du layout
            fig_equip.update_layout(
                yaxis2=dict(
                    title="Taux d'équipement pour 1000 Habitants",
                    overlaying='y',
                    side='right',
                    showgrid=False,
                    range=[0, 8],  # Ajuster l'échelle de 0 à 8
                ),
                height=500,
                legend=dict(
                    orientation="h",  # Légende horizontale
                    yanchor="bottom",
                    y=1.35,  # Position plus haute
                    xanchor="right",
                    x=1,
                    title=dict(text="Capacité")  # Ajout d'un titre à la légende
                ),
                margin=dict(t=150, b=100, l=50, r=50)  # Augmentation de la marge supérieure
            )

            # Affichage du graphique avec une colonne d'aide
            col_chart4, col_help4 = st.columns([1, 0.01])
            with col_chart4:
                st.plotly_chart(fig_equip, use_container_width=True)
            with col_help4:
                st.metric(
                    label="help",
                    value="",
                    help="Ce graphique montre la répartition des lits et places disponibles "
                         "pour une prise en charge médicale, en nombre. "
                         "La ligne orange indique le taux d'équipement des lits, en nombre pour 1000 habitants, "
                         "permettant d'analyser la capacité moyenne disponible dans une zone donnée."
                )

    with tab3:

        # Filtrer les données selon l'année sélectionnée
        if selected_year != "Toutes les années":
            df_filtered = df[df['annee'] == int(selected_year)]
        else:
            df_filtered = df.copy()

        # Filtrer par département si sélectionné
        if selected_region != "Tous les départements":
            df_filtered = df_filtered[df_filtered['nom_region'] == selected_region]

        # Filtrer par pathologie si sélectionnée
        if selected_pathology != "Toutes les pathologies":
            df_filtered = df_filtered[df_filtered['nom_pathologie'] == selected_pathology]
            # Si une pathologie spécifique est sélectionnée, on n'a pas besoin de prendre les N premières
            top_n_patho = [selected_pathology]
        else:
            df_filtered = df_filtered

            # Trouver toutes les pathologies disponibles
            all_patho = df_filtered.groupby('nom_pathologie')['nbr_hospi'].sum().sort_values(ascending=False)

            # Slider pour sélectionner le nombre de pathologies
            nb_patho = st.slider(
                "Nombre de pathologies à afficher",
                min_value=3,
                max_value=10,
                value=5,
                key="nb_patho_age"
            )

            # Sélectionner les N premières pathologies
            top_n_patho = all_patho.head(nb_patho).index.tolist()
        df_topn = df_filtered[df_filtered['nom_pathologie'].isin(top_n_patho)]

        # Définir les colonnes de tranches d'âge
        age_columns = [
            'tranche_age_0_1', 'tranche_age_1_4', 'tranche_age_5_14',
            'tranche_age_15_24', 'tranche_age_25_34', 'tranche_age_35_44',
            'tranche_age_45_54', 'tranche_age_55_64', 'tranche_age_65_74',
            'tranche_age_75_84', 'tranche_age_85_et_plus'
        ]

        # Préparer les données pour le graphique
        graph_data = []
        for _, row in df_topn.iterrows():
            for col in age_columns:
                age_group = col.replace('tranche_age_', '').replace('_', '-')
                if age_group == '85-et-plus':
                    age_group = '85+'
                
                # Calculer le nombre d'hospitalisations pour cette tranche d'âge
                nb_hospi = row['nbr_hospi'] * row[col] / 100
                
                # Formater la tranche d'âge avec "ans"
                display_age = age_group
                if age_group != '85+':
                    display_age = f"{age_group} ans"
                else:
                    display_age = "85 ans et plus"
                
                graph_data.append({
                    'tranche_age': display_age,
                    'pathologie': row['nom_pathologie'],
                    'hospitalisations': nb_hospi,
                    'annee': row['annee']
                })

        # Convertir en DataFrame
        df_graph = pd.DataFrame(graph_data)

        # Grouper les données par année, pathologie et tranche d'âge
        df_scatter = df_graph.groupby(['annee', 'pathologie', 'tranche_age'])['hospitalisations'].sum().reset_index()

        # Ajouter une colonne avec le nombre d'hospitalisations formaté
        df_scatter['hospitalisations_format'] = df_scatter['hospitalisations'].apply(format_number)

        # Créer le graphique animé avec Plotly Express
        fig = px.scatter(df_scatter, 
            x='tranche_age',
            y='hospitalisations',
            animation_frame='annee',
            size='hospitalisations',
            color='pathologie',
            hover_name='pathologie',
            hover_data={
                'pathologie': False,  # Masquer car déjà dans hover_name
                'hospitalisations': False,  # Masquer la version non formatée
                'hospitalisations_format': True,  # Afficher la version formatée
                'tranche_age': True,
                'annee': True
            },
            size_max=50,
            labels={
                'tranche_age': "Tranche d'âge",
                'hospitalisations': "Nombre d'hospitalisations",
                'hospitalisations_format': "Nombre d'hospitalisations",
                'pathologie': 'Pathologie',
                'annee': 'Année'
            },
            title=f"Répartition des hospitalisations par tranche d'âge pour les {len(top_n_patho)} pathologies principales",
        )

        # Personnaliser le layout
        fig.update_traces(
            mode='markers'  # Enlever le texte pour plus de clarté
        )

        fig.update_layout(
            height=600,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=0.94,
                xanchor="right",
                x=1,
                bgcolor='rgba(255,255,255,0.8)'  # Fond légèrement transparent

            ),
            
            # Adaptation automatique de l'axe Y avec une marge de 10%
            yaxis=dict(
                range=[
                    0,
                    df_scatter['hospitalisations'].max() * 1.1  # Ajoute 10% de marge au-dessus
                ]
            ),
            
            # Ajuster la position des contrôles d'animation
            updatemenus=[{
                'type': 'buttons',
                'showactive': False,
                'y': -0.1,
                'x': 0.1,
                'xanchor': 'right',
                'yanchor': 'top',
                'pad': {'t': 0, 'r': 10},
                'buttons': [
                    {
                        'args': [None, {'frame': {'duration': 1500, 'redraw': True}, 'fromcurrent': True}],
                        'label': '▶',
                        'method': 'animate'
                    },
                    {
                        'args': [[None], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate', 'transition': {'duration': 0}}],
                        'label': '⏸',
                        'method': 'animate'
                    }
                ]
            }],
            sliders=[{
                'currentvalue': {
                    'font': {'size': 12},
                    'prefix': 'Année: ',
                    'visible': True,
                    'xanchor': 'right'
                },
                'pad': {'b': 10, 't': 50},
                'len': 0.9,
                'x': 0.1,
                'y': 0.05,
                'transition': {'duration': 1500}
            }],
            xaxis=dict(
                categoryorder='array',
                categoryarray=sorted(df_scatter['tranche_age'].unique(), 
                                  key=lambda x: float(x.split(' ')[0].split('-')[0]))
            )
        )

        # Affichage du graphique avec une colonne d'aide
        col_chart, col_help = st.columns([1, 0.01])
        with col_chart:
            st.plotly_chart(fig, use_container_width=True)
        with col_help:
            st.metric(
                label="help",
                value="",
                help=f"Ce graphique animé montre l'évolution des hospitalisations par tranche d'âge pour les {len(top_n_patho)} pathologies "
                     f"les plus fréquentes{' dans ' + selected_region if selected_region != 'Tous les départements' else ''}. "
                     "La taille des bulles représente le nombre d'hospitalisations. "
                     "Utilisez les contrôles d'animation pour voir l'évolution dans le temps."
            )

        st.markdown("---")

        # Tableau récapitulatif détaillé
        st.subheader("Évolution des pathologies par Sexe - Augmentation les plus importantes (2018-2022)")
        
        # Données filtrées selon le sexe
        df_filtered = df_filtered[df_filtered['sexe'] == selected_sex]

        # Calculer les évolutions année par année
        evolutions_sexe_by_year = {}
        years = sorted(df_filtered['annee'].unique())

        for i in range(len(years) - 1):
            current_year_sexe = years[i]
            next_year_sexe = years[i + 1]
            
            # Données pour l'année courante et suivante
            current_data_sexe = df_filtered[df_filtered['annee'] == current_year_sexe].groupby(['sexe', 'nom_pathologie'])['nbr_hospi'].sum()
            next_data_sexe = df_filtered[df_filtered['annee'] == next_year_sexe].groupby(['sexe', 'nom_pathologie'])['nbr_hospi'].sum()
            
            # Calculer l'évolution en pourcentage
            evolution_sexe = ((next_data_sexe - current_data_sexe) / current_data_sexe * 100).fillna(0)
            evolutions_sexe_by_year[f'{current_year_sexe}-{next_year_sexe}'] = evolution_sexe.dropna()

        # Créer le DataFrame de base avec le nombre total d'hospitalisations
        df_summary_sexe = df_filtered.groupby(['sexe', 'nom_pathologie'])['nbr_hospi'].sum().reset_index()

        # Ajouter les évolutions année par année
        for period, evolution_sexe in evolutions_sexe_by_year.items():
            df_summary_sexe = df_summary_sexe.merge(
                evolution_sexe.reset_index().rename(columns={'nbr_hospi': f'Évol. {period} (%)'}),
                on=['sexe', 'nom_pathologie'],
                how='left'
            )

        # Calculer l'évolution globale (2018-2022)
        hospi_2018_sexe = df_filtered[df_filtered['annee'] == min(years)].groupby(['sexe', 'nom_pathologie'])['nbr_hospi'].sum()
        hospi_2022_sexe = df_filtered[df_filtered['annee'] == max(years)].groupby(['sexe', 'nom_pathologie'])['nbr_hospi'].sum()
        evolution_globale_sexe = ((hospi_2022_sexe - hospi_2018_sexe) / hospi_2018_sexe * 100).fillna(0)
        

        # Ajouter l'évolution globale au DataFrame
        df_summary_sexe = df_summary_sexe.merge(
            evolution_globale_sexe.reset_index().rename(columns={'nbr_hospi': 'Évol. globale (%)'}),
            on=['sexe', 'nom_pathologie'],
            how='left'
        )

        # Trier par évolution globale décroissante
        df_summary_sexe = df_summary_sexe.sort_values('Évol. globale (%)', ascending=False)

        # Colonnes d'évolution pour le gradient
        evolution_sexe_columns = [col for col in df_summary_sexe.columns if 'Évol.' in col]

        # Calculer les min et max des colonnes d'évolution
        evolution_sexe_values = df_summary_sexe[evolution_sexe_columns].values.flatten()
        evolution_sexe_values = evolution_sexe_values[~pd.isna(evolution_sexe_values)]  # Supprime les NaN
        vmin_sexe, vmax_sexe = evolution_sexe_values.min(), evolution_sexe_values.max()

        # Formater et afficher le tableau
        st.dataframe(
            df_summary_sexe.style.format({
                'nbr_hospi': '{:,.0f}',
                **{col: '{:+.1f}%' for col in evolution_sexe_columns}
            }).background_gradient(
                cmap='RdYlGn_r',
                subset=evolution_sexe_columns,
                vmin=vmin_sexe,
                vmax=vmax_sexe
            ),
            use_container_width=True
        )

st.markdown("---")
st.markdown("Développé avec 💫| Le Wagon - Batch #1834 - Promotion 2024")
