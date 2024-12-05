import streamlit as st
import base64
from streamlit_lottie import st_lottie
import requests


# CSS personnalisé pour le style
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #2c3e50;
        padding: 1.5rem 0;
    }
    .section-title {
        color: #34495e;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
        margin: 2rem 0 1rem 0;
    }
    .feature-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Fonction pour afficher un GIF centré
def display_centered_gif(gif_path):
    st.markdown(
        f'<div style="display: flex; justify-content: center;">'
        f'<img src="{gif_path}" width="600px">'
        f'</div>',
        unsafe_allow_html=True
    )

# En-tête
st.markdown("<h1 class='main-title' style='margin-top: -70px; margin-bottom: -8000px;'>🏨 Projet d'analyse et de prédiction hospitalière</h1>", unsafe_allow_html=True)

# Charger et afficher l'animation Lottie
lottie_url = "https://lottie.host/01b53e9b-fb22-4256-b630-fe179a862c14/SpE9Sq2zVA.json"
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_animation = load_lottieurl(lottie_url)
if lottie_animation is not None:
    st.markdown('<div style="margin: -10px 0;">', unsafe_allow_html=True)  
    st_lottie(lottie_animation, speed=1, height=300, key="initial")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.error("Impossible de charger l'animation")
    
# Introduction
st.markdown("""
    <div class="feature-card" style="margin-top: -90px; padding: 1rem;">
    Cette application a été développée dans le cadre d'un projet de Data Analyse au sein du Wagon. 
    Notre équipe a créé cette plateforme interactive pour explorer et analyser les données hospitalières en France, 
    offrant des insights précieux sur différentes spécialités médicales et les tendances d'hospitalisation.
    </div>
""", unsafe_allow_html=True)
# Sections principales
st.markdown('<h2 class="section-title" style="margin-top: -1px;">📊 Fonctionnalités principales</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class="feature-card" style="margin-bottom: -80px;">
        <h3>🎯 Vue générale</h3>
        <p>Explorez les tendances nationales et régionales des hospitalisations en France</p>
        <ul>
            <li><a href="https://medicalcapacity.streamlit.app/Vue_globale" target="_self">Tableaux de bord interactifs</a></li>
            <li><a href="https://medicalcapacity.streamlit.app/Vue_globale" target="_self">Analyses démographiques</a></li>
            <li><a href="https://medicalcapacity.streamlit.app/Vue_globale" target="_self">Indicateurs de performance</a></li>
            <li><a href="https://medicalcapacity.streamlit.app/Vue_globale" target="_self">Comparaisons régionales</a></li>
            <li><a href="https://medicalcapacity.streamlit.app/Vue_globale" target="_self">Évolution temporelle</a></li>
        </ul>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="feature-card" style="margin-bottom: -40px;">
        <h3>⚕️ Focus spécialités</h3>
        <p>Analyses détaillées par spécialité médicale dans le milieu hospitalier</p>
        <ul>
            <li><a href="https://medicalcapacity.streamlit.app/chirurgie" target="_self"> Chirurgie et interventions</a></li>
            <li><a href="https://medicalcapacity.streamlit.app/medecine" target="_self">Médecine générale et spécialisée</a></li>
            <li><a href="https://medicalcapacity.streamlit.app/obstetrique" target="_self">Obstétrique et maternité</a></li>
            <li><a href="https://medicalcapacity.streamlit.app/psy" target="_self">Psychiatrie et santé mentale</a></li>
            <li><a href="https://medicalcapacity.streamlit.app/ssr" target="_self">SSR (Soins de Suite et Réadaptation)</a></li>
            <li><a href="https://medicalcapacity.streamlit.app/esnd" target="_self">ESND (Établissement de Soin Longue Durée)</a></li>
        </ul>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="feature-card">
        <h3>🔮 Outils avancés</h3>
        <p>Fonctionnalités interactives et prédictives</p>
        <ul>
            <li><a href="https://medicalcapacity.streamlit.app/predictions" target="_self">Prédictions hospitalières</a></li>
            <li><a href="https://medicalcapacity.streamlit.app/graph_generator" target="_self">Générateur de graphiques personnalisés</a></li>
            <li><a href="https://medicalcapacity.streamlit.app/docteur_analyste" target="_self">Assistant virtuel IA</a></li>
            <li><a href="https://medicalcapacity.streamlit.app/carte_de_france" target="_self">Cartographie interactive</a></li>

        </ul>
        </div>
    """, unsafe_allow_html=True)

# Méthodologie et Sources
st.markdown('<h2 class="section-title">📚 Méthodologie et sources</h2>', unsafe_allow_html=True)
st.markdown("""
    <div class="feature-card">
    <h3>🔍 Notre approche</h3>
    <p>Cette étude s'appuie sur une méthodologie rigoureuse combinant :</p>
    <ul>
        <li>Analyse statistique approfondie des données hospitalières</li>
        <li>Modélisation prédictive utilisant des algorithmes de machine learning</li>
        <li>Visualisation interactive des données</li>
        <li>Intelligence artificielle pour l'assistance utilisateur</li>
    </ul>
    </div>
""", unsafe_allow_html=True)

# Section Prédictions
st.markdown('<h2 class="section-title";>🎲 Modèles prédictifs</h2>', unsafe_allow_html=True)
st.markdown("""
    <div class="feature-card">
    <h3>📱 Prévisions hospitalières</h3>
    <p>Notre application intègrera bientôt des modèles prédictifs avancés pour :</p>
    <ul>
        <li>Prédire les besoins en lits hospitaliers par région et spécialité</li>
        <li>Anticiper les tendances d'hospitalisation saisonnières</li>
        <li>Optimiser la gestion des capacités hospitalières</li>
        <li>Prévoir les durées moyennes de séjour</li>
    </ul>
    <p><i>Cette fonctionnalité est en cours de développement et sera disponible prochainement.</i></p>
    </div>
""", unsafe_allow_html=True)

# Guide d'utilisation
st.markdown('<h2 class="section-title" style="margin-top: -10px;">📱 Comment utiliser l\'application</h2>', unsafe_allow_html=True)

# Tabs pour le guide d'utilisation
tab1, tab2, tab3 = st.tabs(["⚡ Démarrage", "📱 Analyses", "💫 Conseils"])

with tab1:
    st.markdown("""
        ### Pour commencer
        1. Utilisez la barre de navigation à gauche pour accéder aux différentes sections
        2. Commencez par la "Vue générale" pour une vision d'ensemble
        3. Explorez ensuite les focus spécifiques selon vos intérêts
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("""
        ### Créer vos analyses
        1. Accédez au "Générateur de graphiques"
        2. Sélectionnez vos variables d'intérêt
        3. Personnalisez vos visualisations
        4. Exportez ou partagez vos résultats
    """, unsafe_allow_html=True)

with tab3:
    st.markdown("""
        ### Conseils d'utilisation
        - Utilisez les filtres pour affiner vos recherches
        - N'hésitez pas à combiner différentes visualisations
        - Consultez l'assistant IA pour des analyses approfondies
        - Explorez les comparaisons temporelles et géographiques
    """)

# Section Sources de données
st.markdown('<h2 class="section-title" style="margin-top: -10px;">💾 Sources des données</h2>', unsafe_allow_html=True)
st.markdown("""
    <div class="feature-card">
    <p>Cette analyse s'appuie sur des données officielles de la DREES (Direction de la Recherche, des Études, de l'Évaluation et des Statistiques) :</p>
    
    <ul style="list-style-type: none; padding-left: 0;">
        <li>📊 <a href="https://data.drees.solidarites-sante.gouv.fr/explore/dataset/500_morbidite-hospitaliere/information/">Morbidité hospitalière — DATA.DREES</a></li>
        <li>📈 <a href="https://data.drees.solidarites-sante.gouv.fr/explore/dataset/708_bases-statistiques-sae/information/">Bases statistiques SAE — DATA.DREES</a></li>
        <li>📉 <a href="https://data.drees.solidarites-sante.gouv.fr/explore/dataset/bases-ares/information/">Base ARES - Agrégats régionaux sur les établissements de santé</a></li>
        <li>📑 <a href="https://odin-dataviz-drees.sante.gouv.fr/digdash_dashboard_dataviz_drees/?defaultPage=Morbidit%C3%A9_Hospitali%C3%A8re_Tableau_1_D%C3%A9partements&user=dataviz_sante&pass=dataviz_sante#2">Digdash - Présentation des données Pathologies</a></li>
    </ul>
    </div>
""", unsafe_allow_html=True)

# Section Contact et Aide
st.markdown('<h2 class="section-title" style="margin-top: -10px;">👥 Notre équipe</h2>', unsafe_allow_html=True)
st.markdown("""
    <div class="feature-card">
    Ce projet a été réalisé dans le cadre de la formation Data Analyst au Wagon par :
    
    <br>
    <ul style="list-style-type: none; padding-left: 0;">
        <li>🧑‍💻 <b>Jean-Baptiste Nez</b> - <a href="https://www.linkedin.com/in/jean-baptiste-nez">LinkedIn</a></li>
        <li>👨‍💻 <b>Antonin Bourdelle</b> - <a href="https://www.linkedin.com/in/antonin-bourdelle">LinkedIn</a></li>
        <li>👩‍💻 <b>Astrid Hugonin</b> - <a href="https://www.linkedin.com/in/astrid-hugonin-716a6680/">LinkedIn</a></li>
    </ul>
    </br>

    <p>🎓 Projet de formation Data Analyst - Le Wagon - 2024</p>
    
    <p>⭐ <a href="https://github.com/Jean-Baptiste-N/projet_data_JBN">Voir le projet sur GitHub</a></p>
    </div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("Développé avec 💫| Le Wagon - Batch #1834 - Promotion 2024")
