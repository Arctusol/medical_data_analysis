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
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.agents import AgentExecutor, create_react_agent
from langchain.callbacks.streamlit import StreamlitCallbackHandler
import re
from langchain_core.messages import HumanMessage, AIMessage

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

# Titre de la page et bouton nouvelle conversation
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("<h1 class='main-title' style='margin-top: -50px;'>🤖 Analyste IA</h1>", unsafe_allow_html=True)
with col2:
    if st.button("🔄 Nouvelle discussion", key="new_chat_top"):
        msgs = StreamlitChatMessageHistory(key="langchain_messages")
        msgs.clear()
        st.session_state.messages = []
        st.rerun()

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
            connection_string = f"bigquery://{project_id}/final_dataset"
            
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
                temperature=0,
                streaming=True
            )
            
            # Initialiser la base de données
            db = init_database()
            if db is None:
                return None

            # Create the prompt template with memory
            system_message = """
            Vous êtes un assistant médical spécialisé dans l'analyse des données hospitalières françaises.
            IMPORTANT : Vous devez TOUJOURS répondre en français, jamais en anglais.
            
            AVANT TOUTE ANALYSE :
            1. Si le message contient uniquement des remerciements ou des salutations de fin (comme "merci", "au revoir", "à bientôt", etc.), 
            répondre simplement à l'utilisateur.
            2. Ne PAS faire de requête SQL dans ce cas.
            3. Pour tout autre message, procéder à l'analyse normale selon le format ci-dessous.
            
            🎯 OBJECTIFS :
            1. Répondre aux questions sur les données hospitalières françaises
            2. Analyser les tendances d'hospitalisation par région et département
            3. Fournir des comparaisons temporelles pertinentes (2018-2022)
            4. Identifier les variations significatives dans les indicateurs clés
            
            📋 STRUCTURE DE RÉPONSE :
            Pour chaque analyse, suivre ce format en français :
            
            🏥 Vue d'ensemble (année en cours)
               - Total des hospitalisations sur la zone demandée et la période
               - Durée moyenne de séjour des hospitalisations sur la zone demandée et la période
               - Taux standardisé pour 1000 habitants

            Vue par pathologie (suggestions)
                - Sélection des 5 pathologies les plus fréquentes
                - Nombre d'hospitalisations par pathologie
                - Durée moyenne de séjour
                - Programmées vs Non programmées
                - Comparaison avec 2018
                - Tendances par type de service (classification)
                - Variations des indicateurs clés
            
            Vue par sexe
                - Nombre d'hospitalisations par sexe
                - Durée moyenne de séjour par sexe
                - Comparaison avec 2018
                
            Suggestions d'actions
                - Propose des recherches complémentaires en fonction des variations observées

            ⚡ RÈGLES IMPORTANTES :
            1. Toujours commencer par une vue d'ensemble de l'année 2022
            2. Comparer systématiquement avec 2018 pour l'évolution si possible
            3. Utiliser "Ensemble" pour les analyses générales
            4. Filtrer explicitement sur Homme/Femme pour les comparaisons
            5. Inclure des émojis pertinents pour structurer la réponse
            6. Résumé des points clés en français
            
            📊 INDICATEURS CLÉS À SURVEILLER :
            1. Hospitalisations :
               - Nombre total (nbr_hospi)
               - Durée moyenne (AVG_duree_hospi)
               - Programmées vs Non programmées
            
            2. Performance :
               - Taux standardisé pour 1000 habitants
               - Indice comparatif
               - Durée moyenne de séjour
        
            🔍 FILTRES STANDARDS :
            1. Niveau administratif (colonne : "niveau"):
              - région
               - département
            
            2. Nom du département ou région :
               - Utiliser la colonne nom_region qui contient les deux informations
               - île-de-France s'écrit dans la table : "Ile-de-France"

            2. Temporel :
               - Année principale : 2022
               - Comparaison : 2018
            
            3. Services médicaux (colonne : "classification"):
               - Valeur : M (pour Médecine)
               - Valeur : C (pour Chirurgie)
               - Valeur : SSR (pour Soins de Suite)
               - Valeur : O (pour Obstétrique)
               - Valeur : ESND (pour Soins Longue Durée)
               - Valeur : PSY (pour Psychothérapie)
            
            4. Démographique :
               - Tranches d'âge (0-1 à 85+)
               - Sexe (Homme/Femme/Ensemble)
            
            ⚠️ POINTS D'ATTENTION :
            1. Toujours vérifier la cohérence des données
            2. Signaler les variations importantes (>20%)
            3. Contextualiser les résultats
            4. Proposer des analyses complémentaires pertinentes

            ⚠️ RÈGLES STRICTES :
            1. NE JAMAIS inventer de données si la requête SQL ne retourne rien
            2. Si aucune donnée n'est trouvée, répondre explicitement :
               "Je n'ai pas trouvé de données pour cette requête. Voici les raisons possibles :
               - La pathologie n'existe pas dans la base
               - La période demandée n'est pas couverte
               - La zone géographique n'est pas disponible
               Voulez-vous reformuler votre demande ?"
            3. Ne pas faire d'approximations ou d'extrapolations
            4. Si une métrique est manquante, indiquer "Donnée non disponible"
            5. Toujours indiquer la source exacte des données (année, région)

            🔧 OPTIMISATION DES REQUÊTES SQL :
            1. TOUJOURS utiliser LIMIT 100 maximum pour les requêtes générales
            2. Privilégier les agrégations (GROUP BY) plutôt que les données brutes
            3. Pour les comparaisons temporelles :
               - Utiliser des sous-requêtes avec agrégations
               - Limiter à 2-3 années clés (2018, 2022)
            4. Pour les analyses régionales :
               - Agréger d'abord par région/département
               - Trier par les métriques les plus importantes (ORDER BY)
               - Limiter aux top 5 résultats pertinents
            5. Pour les recherches de pathologies :
               - TOUJOURS utiliser LIKE avec des % (exemple: pathologie LIKE '%Accouchement%')
               - Ne jamais faire de comparaison exacte (pas de pathologie = '...')
               - Utiliser LOWER() pour ignorer la casse (exemple: LOWER(pathologie) LIKE LOWER('%cancer%'))
               - Pour les pathologies complexes, utiliser plusieurs LIKE avec OR
            
            ⚠️ IMPORTANT : Toutes les réponses doivent être en français, y compris les titres, les descriptions et les analyses.
            """
            
            # Create SQL agent
            toolkit = SQLDatabaseToolkit(db=db, llm=llm)
            
            base_agent = create_sql_agent(
                llm=llm,
                db=db,
                agent_type="openai-tools",
                verbose=True,
                prefix=system_message,
                handle_parsing_errors=True
            )
            
            # Create prompt template with history
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_message),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}")
            ])

            # Create chain with prompt and llm
            chain = prompt | base_agent
            
            # Add memory to the chain
            msgs = StreamlitChatMessageHistory(key="langchain_messages")
            agent_with_memory = RunnableWithMessageHistory(
                chain,
                lambda session_id: msgs,
                input_messages_key="input",
                history_messages_key="history"
            )
            
            return agent_with_memory
            
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

    def truncate_messages(messages, max_messages=5):
        """Garde uniquement les n derniers messages pour éviter de dépasser la limite de l'API."""
        return messages[-max_messages:] if len(messages) > max_messages else messages

    def clean_sql_from_message(message):
        """Nettoie le message des données SQL volumineuses."""
        # Si c'est un message assistant, on traite son contenu
        if getattr(message, 'type', None) == 'assistant':
            content = message.content
            # Cherche les requêtes SQL et leurs résultats
            sql_pattern = r"SELECT.*?FROM.*?(?=\n\n|$)"
            content = re.sub(sql_pattern, "[Requête SQL exécutée]", content, flags=re.DOTALL | re.IGNORECASE)
            
            # Limite la taille des résultats de données
            if "```" in content:
                parts = content.split("```")
                for i in range(1, len(parts), 2):  # Traite uniquement les blocs de code
                    if len(parts[i]) > 500:  # Si le bloc de code est trop long
                        parts[i] = parts[i][:500] + "\n... [Résultats tronqués pour l'historique] ..."
                content = "```".join(parts)
            
            # Crée un nouveau message avec le contenu nettoyé
            return HumanMessage(content=message.content) if message.type == "human" else AIMessage(content=content)
        return message

    # StreamHandler for real-time responses
    class StreamHandler(BaseCallbackHandler):
        def __init__(self, container, initial_text=""):
            self.container = container
            self.text = initial_text

        def on_llm_new_token(self, token: str, **kwargs) -> None:
            self.text += token
            self.container.markdown(self.text)

    def main():
        # Initialize the agent if not already done
        if 'agent' not in st.session_state:
            st.session_state.agent = init_agent()
            if st.session_state.agent is None:
                st.error("Impossible d'initialiser l'agent. Veuillez vérifier votre configuration.")
                return
        
        # Initialize message history
        msgs = StreamlitChatMessageHistory(key="langchain_messages")
        if len(msgs.messages) == 0:
            msgs.add_ai_message("Comment puis-je vous aider avec l'analyse des données médicales ?")
        
        # Display chat messages
        for msg in msgs.messages:
            st.chat_message(msg.type).write(msg.content)
        
        # Get user input
        if prompt := st.chat_input("Posez votre question sur les données médicales..."):
            st.chat_message("human").write(prompt)
            
            # Create a placeholder for the AI response
            with st.chat_message("assistant"):
                try:
                    message_container = st.container()
                    st_callback = StreamlitCallbackHandler(message_container)
                    
                    # Get last 2 messages if they exist
                    last_messages = msgs.messages[-2:] if len(msgs.messages) >= 2 else msgs.messages
                    
                    response = st.session_state.agent.invoke(
                        {"input": prompt},
                        {"configurable": {
                            "session_id": "medical_analysis",
                            "history": last_messages
                        },
                        "callbacks": [st_callback]}
                    )
                    
                    final_response = response.get('output', "Je n'ai pas pu générer une réponse.")
                    message_container.markdown(final_response)
                    
                except Exception as e:
                    st.error(f"Une erreur s'est produite : {str(e)}")
                    return

        # Afficher les suggestions après chaque réponse
        if msgs.messages and msgs.messages[-1].type == "assistant":
            with st.container():
                st.markdown("### 💡 Questions suggérées")
                last_user_message = next((msg.content for msg in reversed(msgs.messages) if msg.type == "human"), None)
                if last_user_message:
                    suggestions = get_contextual_suggestions(last_user_message)
                    
                    num_suggestions = len(suggestions)
                    if num_suggestions > 0:
                        cols = st.columns(min(3, num_suggestions))
                        for idx, suggestion in enumerate(suggestions):
                            col_idx = idx % min(3, num_suggestions)
                            with cols[col_idx]:
                                if st.button(suggestion, key=f"sugg_{idx}"):
                                    st.chat_message("human").write(suggestion)
                                    
                                    # Create a placeholder for the AI response
                                    with st.chat_message("assistant"):
                                        message_container = st.container()
                                        try:
                                            st_callback = StreamlitCallbackHandler(message_container)
                                            # Get last 2 messages if they exist
                                            last_messages = msgs.messages[-2:] if len(msgs.messages) >= 2 else msgs.messages
                                            
                                            response = st.session_state.agent.invoke(
                                                {"input": suggestion},
                                                {"configurable": {
                                                    "session_id": "medical_analysis",
                                                    "history": last_messages
                                                },
                                                "callbacks": [st_callback]}
                                            )
                                            final_response = response.get('output', "Je n'ai pas pu générer une réponse.")
                                            message_container.markdown(final_response)
                                            
                                        except Exception as e:
                                            st.error(f"Une erreur s'est produite : {str(e)}")

            # Ajouter le markdown à la fin du chat
            st.markdown("### 📝 Résumé de la discussion")
            st.markdown("""
            Cette interface vous permet d'analyser les données hospitalières françaises de manière interactive. 
            Vous pouvez :
            - Poser des questions en langage naturel sur les données médicales
            - Obtenir des analyses détaillées par région, pathologie ou période
            - Explorer les tendances et comparaisons temporelles
            - Recevoir des suggestions de questions pertinentes
            
            N'hésitez pas à utiliser les suggestions ou à poser vos propres questions !
            """)

        # Bouton pour nouvelle conversation
        if st.button("🔄 Nouvelle conversation"):
            msgs = StreamlitChatMessageHistory(key="langchain_messages")
            msgs.clear()
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

st.markdown("---")
st.markdown("Développé avec 💫| Le Wagon - Batch #1834 - Promotion 2024")