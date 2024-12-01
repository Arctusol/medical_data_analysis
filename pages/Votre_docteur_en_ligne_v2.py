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

# Titre de la page
st.title("Votre Docteur en Ligne V2 - Assistant SQL")

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
            system_message = """Vous êtes un assistant médical spécialisé dans l'analyse des données hospitalières françaises.
Votre rôle est d'aider à comprendre et analyser les tendances en matière d'hospitalisations, de pathologies et de services médicaux.

Pour chaque question, vous devez :
1. Analyser soigneusement la demande de l'utilisateur
2. Créer une requête SQL précise et adaptée pour BigQuery
3. Interpréter les résultats de manière professionnelle et accessible

Règles importantes :
- La table principale est `class_join_total_morbidite_population`
- Utilisez la syntaxe SQL BigQuery (par exemple DATE() pour les dates)
- Limitez les résultats à 10 lignes sauf si spécifié autrement
- Présentez les résultats de manière claire avec des émojis appropriés
- Gardez un ton professionnel car nous parlons de santé
- Proposez des analyses complémentaires pertinentes

Les colonnes principales sont :
- niveau (object) : Niveau administratif (département, région).
- cle_unique (object) : Identifiant unique par enregistrement.
- sexe (object) : Sexe (Homme/Femme/Ensemble).
- year (dbdate) : Date en format AAAA-MM-JJ.
- annee (Int64) : Année (format numérique).
- region (object) : Code ou nom de la région.
- code_region (Int64) : Code numérique de la région.
- nom_region (object) : Nom complet de la région.

Pathologie

- pathologie (object) : Code descriptif de la pathologie.
- code_pathologie (Int64) : Code numérique de la pathologie.
- nom_pathologie (object) : Nom complet de la pathologie.

Hospitalisations

- nbr_hospi (Int64) : Nombre total d’hospitalisations.
- evolution_nbr_hospi (Int64) : Variation absolue du nombre d’hospitalisations.
- evolution_percent_nbr_hospi (float64) : Variation en pourcentage.
- hospi_prog_24h (Int64) : Hospitalisations programmées (24h).
- hospi_autres_24h (Int64) : Autres hospitalisations (24h).
- hospi_total_24h (Int64) : Total hospitalisations en 24h.
- 18-29. hospi_1J à hospi_30J (Int64) : Durées d’hospitalisation (jours spécifiques ou plages).
- hospi_total_jj (Int64) : Total hospitalisations, toutes durées confondues.
- total_hospi (Int64) : Nombre global d’hospitalisations.
- AVG_duree_hospi (float64) : Durée moyenne des hospitalisations.

Évolution hospitalière

- 33-39. evolution_hospi_* (Int64, float64) : Variations absolues et en pourcentage des différents indicateurs hospitaliers (24h, total, durée moyenne, etc.).
Tranches d’âge

- 40-50. tranche_age_* (float64) : Proportions d’hospitalisations par tranche d’âge (de 0-1 an à 85 ans et plus).

Taux et indices

- tx_brut_tt_age_pour_mille (float64) : Taux brut pour 1 000 habitants.
- tx_standard_tt_age_pour_mille (float64) : Taux standardisé pour 1 000 habitants.
- indice_comparatif_tt_age_percent (float64) : Indice standardisé en pourcentage.
- 54 à 59. evolution_tx_* (float64) : Variations de taux brut, standardisé, et indices comparatifs en pourcentage.
Divers
- classification (object) : Classification en terme de service médical : M (Médecine), C (Chirurgie), SSR (soins de suite et de réadaptation), O (Obstétrique), ESND (Établissement de santé non défini), PSY (Psychothérapie).
- population (Int64) : Population totale associée par région et département (valeurs dupliqués).
- evolution_percent_indice_comparatif_tt_age_percent (float64) : Variation en pourcentage de l'indice comparatif pour tous âges.

N'hésitez pas à croiser les données pour fournir des analyses pertinentes.
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
            'start': "🤔 Je réfléchis à votre question...",
            'analyzing': "🔍 J'analyse les données médicales pertinentes...",
            'querying': "📊 J'extrais les informations de la base de données...",
            'formatting': "✨ Je formule une réponse claire et détaillée..."
        }
        placeholder.markdown(thinking_states.get(step, "🤔 Je réfléchis..."))
        time.sleep(1)  # Petit délai pour rendre les transitions visibles

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
                        # Étape 1: Début de la réflexion
                        update_thinking_status(message_placeholder, 'start')
                        
                        # Étape 2: Analyse de la question
                        update_thinking_status(message_placeholder, 'analyzing')
                        response = st.session_state.agent.invoke(prompt)
                        
                        # Étape 3: Requête et traitement
                        update_thinking_status(message_placeholder, 'querying')
                        final_response = response.get('output', "Je n'ai pas pu générer une réponse.")
                        
                        # Étape 4: Formatage de la réponse
                        update_thinking_status(message_placeholder, 'formatting')
                        time.sleep(0.5)
                        
                        # Affichage de la réponse finale
                        message_placeholder.markdown(final_response)
                        
                        # Ajouter la réponse à l'historique
                        st.session_state.messages.append({"role": "assistant", "content": final_response})
                        st.rerun()
                    
                    except Exception as e:
                        message_placeholder.markdown(f"❌ Désolé, une erreur s'est produite : {str(e)}")

        # Afficher les suggestions après chaque réponse
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
            with suggestions_container:
                st.markdown("### 💡 Pour approfondir :")
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
                                        update_thinking_status(message_placeholder, 'start')
                                        update_thinking_status(message_placeholder, 'analyzing')
                                        response = st.session_state.agent.invoke(suggestion)
                                        update_thinking_status(message_placeholder, 'querying')
                                        final_response = response.get('output', "Je n'ai pas pu générer une réponse.")
                                        update_thinking_status(message_placeholder, 'formatting')
                                        time.sleep(0.5)
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
