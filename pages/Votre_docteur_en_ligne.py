import streamlit as st
from langchain_openai import AzureChatOpenAI
import pandas as pd
from google.cloud import bigquery


# Chargement des données
@st.cache_resource
def fetch_data():
    try:
        # Chargement des secrets
        gcp_service_account = st.secrets["gcp_service_account"]
        client = bigquery.Client.from_service_account_info(gcp_service_account)
        
        # Chargement du dataset principal
        df_complet = client.query('''
            SELECT * FROM `projet-jbn-data-le-wagon.dbt_medical_analysis_join_total_morbidite.class_join_total_morbidite_population`
        ''').to_dataframe()
        
        # Convertir les colonnes year en datetime
        df_complet['year'] = pd.to_datetime(df_complet['year'])
        
        # Créer des vues spécifiques
        df_nbr_hospi = df_complet[[
            'year', 'region', 'nom_region', 'pathologie', 'nom_pathologie', 'sexe',
            'nbr_hospi', 'evolution_nbr_hospi', 'evolution_percent_nbr_hospi',
            'hospi_prog_24h', 'hospi_autres_24h', 'hospi_total_24h'
        ]].copy()

        df_duree_hospi = df_complet[[
            'year', 'region', 'nom_region', 'pathologie', 'nom_pathologie',
            'AVG_duree_hospi', 'evolution_AVG_duree_hospi', 'evolution_percent_AVG_duree_hospi'
        ]].copy()
        
        # Charger les données de capacité
        df_capacite_hospi = client.query('''
            SELECT * FROM `projet-jbn-data-le-wagon.dbt_medical_analysis_join_total_morbidite_capacite.class_join_total_morbidite_capacite`
        ''').to_dataframe()
        
        # Convertir la colonne year en datetime pour df_capacite_hospi
        df_capacite_hospi['year'] = pd.to_datetime(df_capacite_hospi['year'])
        
        return df_nbr_hospi, df_duree_hospi, df_capacite_hospi, df_complet
        
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {str(e)}")
        return None, None, None, None

# Chargement des données
df_nbr_hospi, df_duree_hospi, df_capacite_hospi, df_complet = fetch_data()

st.title(" Parle avec un docteur 👨‍⚕️")


def get_data_context():
    context = []
    
    try:
        if not df_nbr_hospi.empty:
            years = sorted(df_nbr_hospi['year'].dt.year.unique())
            
            # Créer un dictionnaire de données par année
            data_by_year = {}
            for year in years:
                year_data = {}
                
                # Données d'hospitalisation pour l'année
                year_hospi = df_nbr_hospi[df_nbr_hospi['year'].dt.year == year]
                year_data['total_hospi'] = year_hospi['nbr_hospi'].sum()
                year_data['prog_24h'] = year_hospi['hospi_prog_24h'].sum()
                year_data['autres_24h'] = year_hospi['hospi_autres_24h'].sum()
                
                # Durée moyenne pour l'année
                year_duree = df_duree_hospi[df_duree_hospi['year'].dt.year == year]
                year_data['avg_duration'] = year_duree['AVG_duree_hospi'].mean()
                
                # Top 5 régions pour l'année
                top_regions = year_hospi.groupby('nom_region')['nbr_hospi'].sum().nlargest(5).to_dict()
                year_data['top_regions'] = top_regions
                
                # Services pour l'année
                services_data = {}
                for code, nom in {
                    'M': 'Médecine',
                    'C': 'Chirurgie',
                    'SSR': 'Soins de suite et réadaptation',
                    'O': 'Obstétrique',
                    'PSY': 'Psychiatrie',
                    'ESND': 'Établissement de soin longue durée'
                }.items():
                    service_data = df_complet[
                        (df_complet['classification'] == code) & 
                        (df_complet['year'].dt.year == year)
                    ]
                    if not service_data.empty:
                        services_data[nom] = service_data['nbr_hospi'].sum()
                year_data['services'] = services_data
                
                # Top 10 pathologies pour l'année
                top_pathologies = year_hospi.groupby('nom_pathologie')['nbr_hospi'].sum().nlargest(10).to_dict()
                year_data['top_pathologies'] = top_pathologies
                
                data_by_year[year] = year_data
            
            # Information générale
            context.append("📊 Données disponibles par année:")
            context.append(f"- Période couverte: de {min(years)} à {max(years)}")
            context.append("\nPour chaque année, vous avez accès aux informations suivantes:")
            context.append("- Nombre total d'hospitalisations")
            context.append("- Hospitalisations programmées et non programmées")
            context.append("- Durée moyenne des séjours")
            context.append("- Top 5 des régions")
            context.append("- Répartition par service médical")
            context.append("- Top 10 des pathologies")
            context.append("\nUtilisez ces données en spécifiant l'année souhaitée dans votre réponse.")
            
            # Ajouter le dictionnaire de données au contexte
            context.append("\nDonnées détaillées par année:")
            context.append(str(data_by_year))
    
    except Exception as e:
        context.append("⚠️ Certaines données ne sont pas disponibles pour le moment.")
        st.error(f"Erreur lors de la récupération du contexte : {str(e)}")
    
    return "\n".join(context)

def get_ai_response(prompt):
    context = get_data_context()
    
    # Construire l'historique de la conversation
    conversation_history = ""
    if "messages" in st.session_state and len(st.session_state.messages) > 0:
        for msg in st.session_state.messages:
            role = "Assistant" if msg["role"] == "assistant" else "Patient"
            conversation_history += f"{role}: {msg['content']}\n"
    
    enhanced_prompt = f"""En tant qu'assistant spécialisé dans le domaine hospitalier français, je vais vous aider en me basant sur les données suivantes :

{context}

Historique de la conversation:
{conversation_history}

Nouvelle question du patient : {prompt}

Directives pour la réponse :
1. Utilisez les données fournies de manière précise, sans interprétation excessive.
2. Lorsque l'utilisateur demande des informations sur une valeur, vous pouvez fournir des comparaisons avec l'annee precedente.
3. Lorsque l'utilisateur demande des informations sur une région ou département spécifique, vous devez fournir des comparaisons avec d'autres regions ou departements.
4. Structurez votre réponse de manière claire avec des émojis appropriés. Le ton ne doit pas être joyeux car on parle de maladie et de personnes. Les émoticônes peuvent aider mais sont là pour accentuer le message.
5. Proposez ensuite à l'utilisateur des actions qu'il pourrra choisir grâce au numéro de l'action. Voici des exemples qui doivent être adaptés à chaque questions de l'utilisateur afin qu'il n'obtienne pas de résultats inutiles et deux fois la même réponse:
   - La tendance des hospitalisations
   - Les comparaisons avec l'année précédente
   - La répartition par service médical
   - Les spécificités géographiques
   - Les durées moyennes de séjour
6. Utilisez des termes simples et accessibles
7. Si une information n'est pas disponible dans les données, précisez-le clairement

Veuillez répondre de manière concise et factuelle tels un médecin."""
    
    try:
        llm = AzureChatOpenAI(
            openai_api_version="2023-05-15",
            azure_deployment=st.secrets["azure"]["AZURE_DEPLOYMENT_NAME"],
            azure_endpoint=st.secrets["azure"]["AZURE_ENDPOINT"],
            api_key=st.secrets["azure"]["AZURE_API_KEY"],
            temperature=0.2
        )
        response = llm.invoke(enhanced_prompt)
        return str(response.content) if hasattr(response, 'content') else str(response)
    except Exception as e:
        st.error(f"Error: Make sure your Azure OpenAI credentials are properly set in .streamlit/secrets.toml. Error details: {str(e)}")
        return None

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Create containers first
chat_container = st.container()
input_container = st.container()

# Suggestions de questions
st.markdown("### 💡 Que voulez-vous savoir ?")
questions_container = st.container()
col1, col2 = questions_container.columns(2)

with col1:
    if st.button("🏥 Quelle est la tendance des hospitalisations en France ?"):
        question = "Quelle est la tendance des hospitalisations en France ?"
        st.session_state.messages.append({"role": "user", "content": question})
        response = get_ai_response(question)
        if response:
            st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
    
    if st.button("📊 Quelle région a le plus d'hospitalisations ?"):
        question = "Quelle région a le plus d'hospitalisations ?"
        st.session_state.messages.append({"role": "user", "content": question})
        response = get_ai_response(question)
        if response:
            st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

with col2:
    if st.button("⏱️ Quelle est la durée moyenne d'hospitalisation ?"):
        question = "Quelle est la durée moyenne d'hospitalisation en Gironde ?"
        st.session_state.messages.append({"role": "user", "content": question})
        response = get_ai_response(question)
        if response:
            st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
    
    if st.button("📋 Y a-t-il plus d'hospitalisations programmées ou non programmées ?"):
        question = "Y a-t-il plus d'hospitalisations programmées ou non programmées ?"
        st.session_state.messages.append({"role": "user", "content": question})
        response = get_ai_response(question)
        if response:
            st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

# Display chat messages in the chat container
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Place the input at the bottom
with input_container:
    if prompt := st.chat_input("Posez votre question sur le milieu hospitalier..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        response = get_ai_response(prompt)
        if response:
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

st.markdown("---")
# Ajouter un second bouton "Nouvelle conversation" en bas de la page
if st.button("🔄 Nouvelle conversation", key="new_conversation_bottom"):
    st.session_state.messages = []
    st.rerun()