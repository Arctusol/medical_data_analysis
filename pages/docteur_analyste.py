import streamlit as st
from langchain_openai import AzureChatOpenAI
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain import hub
from google.cloud import bigquery
import pandas as pd
import os
from sqlalchemy.engine import create_engine
from sqlalchemy_bigquery import BigQueryDialect
import time
from streamlit_lottie import st_lottie

MAIN_COLOR = "#FF4B4B"

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
    .thinking-animation {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 10px 0;
    }
    </style>
    <script src="https://unpkg.com/@lottiefiles/lottie-player@2.0.8/dist/lottie-player.js"></script>
""", unsafe_allow_html=True)

# Titre de la page
st.markdown("<h1 class='main-title' style='margin-top: -50px;'>🤖 Analyste IA</h1>", unsafe_allow_html=True)

try:
    # Configuration Azure OpenAI
    AZURE_CONFIG = {
        "api_version": "2023-05-15",
        "azure_endpoint": st.secrets["azure"]["AZURE_ENDPOINT"],
        "azure_deployment": st.secrets["azure"]["AZURE_DEPLOYMENT_NAME"],
        "api_key": st.secrets["azure"]["AZURE_API_KEY"]
    }

    @st.cache_resource
    def init_database():
        """Initialise la connexion à la base de données.""" 
        try:
            # Chargement des secrets
            gcp_service_account = st.secrets["gcp_service_account"]
            project_id = gcp_service_account["project_id"]
            
            # Créer l'URL de connexion BigQuery
            connection_string = f"bigquery://{project_id}/dbt_medical_analysis_join_total_morbidite"
            
            # Créer le moteur SQLAlchemy avec les credentials
            engine = create_engine(
                connection_string,
                credentials_info=gcp_service_account
            )
            
            # Créer la connexion SQLDatabase pour LangChain
            db = SQLDatabase(engine)
            
            return db
            
        except Exception as e:
            st.error(f"Erreur de connexion à la base de données : {str(e)}")
            return None

    @st.cache_resource
    def init_agent():
        """Initialise l'agent LangChain.""" 
        try:
            # Initialiser le modèle LLM
            llm = AzureChatOpenAI(
                azure_endpoint=AZURE_CONFIG["azure_endpoint"],
                azure_deployment=AZURE_CONFIG["azure_deployment"],
                openai_api_version=AZURE_CONFIG["api_version"],
                api_key=AZURE_CONFIG["api_key"],
                temperature=0
            )
            
            # Initialiser la base de données
            db = init_database()
            if not db:
                return None
                
            # Créer la boîte à outils SQL
            toolkit = SQLDatabaseToolkit(db=db, llm=llm)
            
            # Créer un prompt système personnalisé pour le contexte médical
            system_message = """
            Vous êtes un assistant médical spécialisé dans l'analyse des données hospitalières françaises.
            Votre rôle est d'aider à comprendre et analyser les tendances en matière d'hospitalisations, de pathologies et de services médicaux.

            Pour chaque question, vous devez :
            1. Analyser soigneusement la demande de l'utilisateur
            2. Créer une requête SQL précise et adaptée pour BigQuery
            3. Interpréter les résultats de manière professionnelle et accessible
            4. Proposer des analyses complémentaires pertinentes
            5. Fournir des visualisations claires et appropriées pour aider l'utilisateur
            6. Réponds à l'utilisateur en Français uniquement

            Règles importantes :
            - Les tables principales sont :
              * `class_join_total_morbidite_sexe_population` (données principales)
              * `class_join_total_morbidite_capacite_kpi` (données de capacité)
            - Utilisez la syntaxe SQL BigQuery (par exemple DATE() pour les dates)
            - Limitez les résultats à 10 lignes sauf si spécifié autrement
            - Présentez les résultats de manière claire avec des émojis appropriés
            - Gardez un ton professionnel car nous parlons de santé
            - Proposez des analyses complémentaires pertinentes

            Structure des données principales :
            
            1. Identification et Localisation
            - niveau (STRING) : Niveau administratif (département, région)
            - cle_unique (STRING) : Identifiant unique par enregistrement
            - sexe (STRING) : Homme/Femme/Ensemble
            - year (DATE) : Format AAAA-MM-JJ
            - annee (INTEGER) : Année en format numérique
            - region (STRING) : Code ou nom de la région
            - code_region (INTEGER) : Code numérique de la région
            - nom_region (STRING) : Nom complet de la région

            2. Pathologie
            - pathologie (STRING) : Code descriptif de la pathologie
            - code_pathologie (INTEGER) : Code numérique de la pathologie
            - nom_pathologie (STRING) : Nom complet de la pathologie

            3. Hospitalisations
            - nbr_hospi (INTEGER) : Nombre total d'hospitalisations
            - hospi_prog_24h (FLOAT) : Hospitalisations programmées (24h)
            - hospi_autres_24h (FLOAT) : Autres hospitalisations (24h)
            - hospi_total_24h (FLOAT) : Total hospitalisations en 24h
            - hospi_[1-9]J (FLOAT) : Hospitalisations par durée (1-9 jours)
            - hospi_10J_19J (FLOAT) : Hospitalisations de 10 à 19 jours
            - hospi_20J_29J (FLOAT) : Hospitalisations de 20 à 29 jours
            - hospi_30J (FLOAT) : Hospitalisations de 30 jours et plus
            - hospi_total_jj (FLOAT) : Total toutes durées confondues
            - AVG_duree_hospi (FLOAT) : Durée moyenne des hospitalisations

            4. Données Démographiques
            Les données démographiques sont exprimées en proportions (FLOAT) pour chaque tranche d'âge :
            - tranche_age_0_1 : Nourrissons (0 à 1 an)
            - tranche_age_1_4 : Jeunes enfants (1 à 4 ans)
            - tranche_age_5_14 : Enfants (5 à 14 ans)
            - tranche_age_15_24 : Adolescents et jeunes adultes (15 à 24 ans)
            - tranche_age_25_34 : Jeunes adultes (25 à 34 ans)
            - tranche_age_35_44 : Adultes (35 à 44 ans)
            - tranche_age_45_54 : Adultes matures (45 à 54 ans)
            - tranche_age_55_64 : Seniors actifs (55 à 64 ans)
            - tranche_age_65_74 : Jeunes retraités (65 à 74 ans)
            - tranche_age_75_84 : Personnes âgées (75 à 84 ans)
            - tranche_age_85_et_plus : Personnes très âgées (85 ans et plus)

            Ces proportions permettent d'analyser :
            - La répartition des hospitalisations par âge
            - Les tendances spécifiques à certaines tranches d'âge
            - La comparaison entre différentes régions ou services médicaux
            - L'évolution temporelle de la structure d'âge des patients

            5. Indicateurs de Santé
            - tx_brut_tt_age_pour_mille (FLOAT) : Taux brut pour 1 000 habitants
            - tx_standard_tt_age_pour_mille (FLOAT) : Taux standardisé pour 1 000 habitants
            - indice_comparatif_tt_age_percent (FLOAT) : Indice standardisé en pourcentage

            6. Classification et Population
            - classification (STRING) : Service médical :
              * M (Médecine)
              * C (Chirurgie)
              * SSR (Soins de Suite et de Réadaptation)
              * O (Obstétrique)
              * ESND (Établissement de Soin Longue Durée)
              * PSY (Psychothérapie)

            - population (INTEGER) : Population totale par département

            Données de capacité (table class_join_total_morbidite_capacite_kpi) :
            
            1. Capacité d'Accueil
            - lit_hospi_complete (FLOAT) : Nombre de lits en hospitalisation complète
            - place_hospi_partielle (FLOAT) : Nombre de places en hospitalisation partielle
            - passage_urgence (FLOAT) : Nombre de passages aux urgences

            2. Activité Hospitalière
            - sejour_hospi_complete (FLOAT) : Nombre de séjours en hospitalisation complète
            - sejour_hospi_partielle (FLOAT) : Nombre de séjours en hospitalisation partielle
            - journee_hospi_complete (FLOAT) : Nombre de journées d'hospitalisation complète

            N'hésitez pas à croiser les données entre les tables pour fournir des analyses pertinentes.
            """
            
            # Créer l'agent SQL avec le prompt personnalisé
            agent = create_sql_agent(
                llm=llm,
                toolkit=toolkit,
                verbose=True,
                agent_type="openai-tools",
                prefix=system_message
            )
            
            return agent
            
        except Exception as e:
            st.error(f"Erreur d'initialisation de l'agent : {str(e)}")
            return None

    def update_thinking_status(placeholder, step):
        """Met à jour le statut de réflexion de l'agent.""" 
        thinking_states = {
            'start': "Initialisation de l'analyse",
            'understanding': "Compréhension de votre question",
            'processing': "Traitement des informations hospitalières",
            'querying': "Extraction des données pertinentes",
            'calculating': "Calcul des statistiques médicales",
            'validating': "Validation des résultats",
            'formatting': "Formulation de la réponse"
        }
        
        lottie_url = "https://lottie.host/e4d1342b-0eb1-4182-9379-5859487f040d/b9l2rzI7Nh.json"
        
        with placeholder:
            st_lottie(lottie_url, height=300)

    def get_contextual_suggestions(user_input):

        templates = {
            "pathologie": ["Quelles pathologies sont les plus fréquentes ?", "Évolution des hospitalisations par pathologie ?", "Comparaison des régions sur les pathologies."],
            "region": ["Quelles régions ont le plus d'hospitalisations ?", "Comparer les régions sur le taux brut.", "Top régions selon l'indice standardisé."],
            "année": ["Tendances des hospitalisations pour l'année spécifiée ?", "Comment le taux brut évolue-t-il sur plusieurs années ?", "Focus sur une région pour une année spécifique ?"]
        }
        
        # Analyse simple du contexte via mots-clés
        context = []
        if any(word in user_input.lower() for word in ["pathologie", "maladie", "diagnostic"]):
            context.append("pathologie")
        if any(word in user_input.lower() for word in ["région", "département", "localisation"]):
            context.append("region")
        if any(word in user_input.lower() for word in ["année", "évolution", "tendance"]):
            context.append("année")
        
        # Combine les suggestions pertinentes
        suggestions = [template for key in context for template in templates.get(key, [])]
        return suggestions if suggestions else ["Besoin d'aide pour poser une question ?"]

    def main():
        # Initialiser l'historique des messages
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Créer les containers
        chat_container = st.container()
        suggestions_container = st.container()
        input_container = st.container()

        # Afficher l'historique des messages dans le chat container
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Gérer l'entrée utilisateur
        with input_container:
            if prompt := st.chat_input("Posez votre question sur les données médicales..."):
                # Ajouter la question à l'historique
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                # Afficher la question
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                # Afficher le message "en cours de réflexion"
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    
                    try:

                        update_thinking_status(message_placeholder, 'validating')
                        response = st.session_state.agent.invoke(prompt)


                        final_response = response.get('output', "Je n'ai pas pu générer une réponse.")
                        message_placeholder.markdown(final_response)
                        
                        # Ajouter la réponse à l'historique
                        st.session_state.messages.append({"role": "assistant", "content": final_response})
                        st.rerun()
                    
                    except Exception as e:
                        message_placeholder.markdown(f"❌ Désolé, une erreur s'est produite : {str(e)}")

        # Afficher les suggestions après chaque réponse
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
            with suggestions_container:
                st.markdown("### 💬 Discussion")
                suggestions = get_contextual_suggestions(st.session_state.messages[-2]["content"])  # Get suggestions based on last user message
                
                # Créer des colonnes pour les suggestions
                num_suggestions = len(suggestions)
                if num_suggestions > 0:
                    cols = st.columns(min(3, num_suggestions))  # Maximum 3 colonnes
                    for idx, suggestion in enumerate(suggestions):
                        col_idx = idx % min(3, num_suggestions)
                        with cols[col_idx]:
                            if st.button(suggestion, key=f"sugg_{idx}"):
                                st.session_state.messages.append({"role": "user", "content": suggestion})
                                with st.chat_message("user"):
                                    st.markdown(suggestion)
                                 
                                with st.chat_message("assistant"):
                                    message_placeholder = st.empty()
                                    try:
                                        response = st.session_state.agent.invoke(prompt)

                                        final_response = response.get('output', "Je n'ai pas pu générer une réponse.")
                                        message_placeholder.markdown(final_response)
                                        st.session_state.messages.append({"role": "assistant", "content": final_response})
                                        st.rerun()
                                    except Exception as e:
                                        message_placeholder.markdown(f"❌ Désolé, une erreur s'est produite : {str(e)}")

        # Bouton pour nouvelle conversation
        if st.button("🔄 Nouvelle conversation"):
            st.session_state.messages = []
            st.rerun()

    # Initialisation uniquement si tous les imports sont disponibles
    if 'agent' not in st.session_state:
        db = init_database()
        if db is not None:
            st.session_state.agent = init_agent()

    # Interface utilisateur
    main()

except ImportError as e:
    st.error(f"Certains packages requis ne sont pas installés : {str(e)}")
    st.info("Assurez-vous d'avoir installé tous les packages nécessaires : langchain-openai, langchain-community, sqlalchemy-bigquery")
except Exception as e:
    st.error(f"Une erreur s'est produite : {str(e)}")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("pages/gooey.ai - ultra detailed 8k cg hospital medical room equipment.png", width=600)
    
st.markdown("---")
st.markdown("Développé avec 💫|  Le Wagon - Batch #1834 - Promotion 2024")
