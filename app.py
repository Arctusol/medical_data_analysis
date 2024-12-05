import streamlit as st

# Configuration de la page - doit être la première commande Streamlit
st.set_page_config(
    page_title="Analyse Hospitalière",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="auto"
)

# Organisation des pages
home = st.Page("pages/Home.py", title="Accueil", icon="🏠", default=True)
vue_globale = st.Page("pages/Vue_globale.py", title="Vue générale", icon="🏥")
carte_de_france = st.Page("pages/carte_de_france.py", title="Carte de France", icon="🌍")
chatSQL = st.Page("pages/docteur_analyste.py", title="Votre assistant virtuel", icon="👨‍⚕️")
chirurgie = st.Page("pages/chirurgie.py", title="Chirurgie", icon="👨‍⚕️")
medecine = st.Page("pages/medecine.py", title="Médecine", icon="⚕️")
obstetrique = st.Page("pages/obstetrique.py", title="Obstétrique", icon="👶")
esdn = st.Page("pages/esnd.py", title="ESND", icon="🏥")
psy = st.Page("pages/psy.py", title="Psychiatrie", icon="🧠")
ssr = st.Page("pages/ssr.py", title="SSR", icon="♿")
graphs = st.Page("pages/graph_generator.py", title="Générateur de graphiques", icon="📊")
predictif = st.Page("pages/predictions.py", title="Modèles de prédiction", icon="📊")

# Organisation en sections
pg = st.navigation({
    "Accueil": [home],
    "Vue générale en France": [vue_globale, carte_de_france],
    "Vue par service médical": [chirurgie, medecine, obstetrique, psy, ssr, esdn],
    "Modèles prédictifs": [predictif],
    "Outils": [graphs, chatSQL]
})

# Exécution de la page sélectionnée
pg.run()
