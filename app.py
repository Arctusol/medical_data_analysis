import streamlit as st
import streamlit.components.v1 as components
from bs4 import BeautifulSoup
import shutil
import pathlib
import logging

# Configuration de la page - doit être la première commande Streamlit
st.set_page_config(
    page_title="Analyse Hospitalière",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="auto"
)

def add_analytics():
    GA_ID = "GTM-NBHTFL6M"
    analytics_js = f"""
    <!-- Google Tag Manager -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{GA_ID}');
    </script>
    <div id="{GA_ID}"></div>
    """
    
    # Identify html path of streamlit
    index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
    logging.info(f'editing {index_path}')
    soup = BeautifulSoup(index_path.read_text(), features="html.parser")
    if not soup.find(id=GA_ID):  # if id not found within html file
        bck_index = index_path.with_suffix('.bck')
        if bck_index.exists():
            shutil.copy(bck_index, index_path)  # backup recovery
        else:
            shutil.copy(index_path, bck_index)  # save backup
        html = str(soup)
        new_html = html.replace('<head>', '<head>\n' + analytics_js)
        index_path.write_text(new_html)  # insert analytics tag at top of head

# Add analytics
add_analytics()


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
predictif = st.Page("pages/predictions.py", title="Modèles de prédiction", icon="📊")

# Organisation en sections
pg = st.navigation({
    "Accueil": [home],
    "Vue générale en France": [vue_globale, carte_de_france],
    "Vue par service médical": [chirurgie, medecine, obstetrique, psy, ssr, esdn],
    "Modèles prédictifs": [predictif],
    "Outils": [chatSQL]
})

# Exécution de la page sélectionnée
pg.run()
