# Documentation Analyse Médicale JBN

## Structure des données

### Table Principale : `class_join_total_morbidite_sexe_population`

#### 1. Identification et Localisation
| Champ | Type | Description |
|-------|------|-------------|
| niveau | STRING | Niveau administratif (département, région) |
| cle_unique | STRING | Identifiant unique par enregistrement |
| sexe | STRING | Homme/Femme/Ensemble |
| year | DATE | Format AAAA-MM-JJ |
| annee | INTEGER | Année en format numérique |
| region | STRING | Code ou nom de la région |
| code_region | INTEGER | Code numérique de la région |
| nom_region | STRING | Nom complet de la région |

#### 2. Pathologie
| Champ | Type | Description |
|-------|------|-------------|
| pathologie | STRING | Code descriptif de la pathologie |
| code_pathologie | INTEGER | Code numérique de la pathologie |
| nom_pathologie | STRING | Nom complet de la pathologie |

#### 3. Hospitalisations
| Champ | Type | Description |
|-------|------|-------------|
| nbr_hospi | INTEGER | Nombre total d'hospitalisations |
| hospi_prog_24h | FLOAT | Hospitalisations programmées (24h) |
| hospi_autres_24h | FLOAT | Autres hospitalisations (24h) |
| hospi_total_24h | FLOAT | Total hospitalisations en 24h |
| hospi_[1-9]J | FLOAT | Hospitalisations par durée (1-9 jours) |
| hospi_10J_19J | FLOAT | Hospitalisations de 10 à 19 jours |
| hospi_20J_29J | FLOAT | Hospitalisations de 20 à 29 jours |
| hospi_30J | FLOAT | Hospitalisations de 30 jours et plus |
| hospi_total_jj | FLOAT | Total toutes durées confondues |
| AVG_duree_hospi | FLOAT | Durée moyenne des hospitalisations |

#### 4. Évolutions et Variations
| Champ | Type | Description |
|-------|------|-------------|
| evolution_nbr_hospi | FLOAT | Variation absolue du nombre d'hospitalisations comparé à l'année précédente|
| evolution_percent_nbr_hospi | FLOAT | Variation en pourcentage comparé à l'année précédente|
| evolution_hospi_total_24h | FLOAT | Évolution des hospitalisations 24h comparé à l'année précédente|
| evolution_hospi_total_jj | FLOAT | Évolution du total des journées comparé à l'année précédente|
| evolution_AVG_duree_hospi | FLOAT | Évolution de la durée moyenne comparé à l'année précédente|
| evolution_percent_* | FLOAT | Variations en pourcentage des différents indicateurs comparé à l'année précédente|

#### 5. Données Démographiques
| Champ | Type | Description |
|-------|------|-------------|
| tranche_age_0_1 | FLOAT | Proportion 0-1 an |
| tranche_age_1_4 | FLOAT | Proportion 1-4 ans |
| tranche_age_5_14 | FLOAT | Proportion 5-14 ans |
| tranche_age_15_24 | FLOAT | Proportion 15-24 ans |
| tranche_age_25_34 | FLOAT | Proportion 25-34 ans |
| tranche_age_35_44 | FLOAT | Proportion 35-44 ans |
| tranche_age_45_54 | FLOAT | Proportion 45-54 ans |
| tranche_age_55_64 | FLOAT | Proportion 55-64 ans |
| tranche_age_65_74 | FLOAT | Proportion 65-74 ans |
| tranche_age_75_84 | FLOAT | Proportion 75-84 ans |
| tranche_age_85_et_plus | FLOAT | Proportion 85 ans et plus |

#### 6. Indicateurs de Santé
| Champ | Type | Description |
|-------|------|-------------|
| tx_brut_tt_age_pour_mille | FLOAT | Taux brut pour 1 000 habitants |
| tx_standard_tt_age_pour_mille | FLOAT | Taux standardisé pour 1 000 habitants |
| indice_comparatif_tt_age_percent | FLOAT | Indice standardisé en pourcentage |

#### 7. Classification et Population
| Champ | Type | Description |
|-------|------|-------------|
| classification | STRING | Service médical (M, C, SSR, O, ESND, PSY)* |
| population | INTEGER | Population totale par département |

\* Classification des services :
- M : Médecine
- C : Chirurgie
- SSR : Soins de Suite et de Réadaptation
- O : Obstétrique
- ESND : Établissement de Soin Longue Durée
- PSY : Psychothérapie

### Table des Capacités : `projet-jbn-data-le-wagon.dbt_medical_analysis_join_total_morbidite_capacite.class_join_total_morbidite_capacite_kpi`

#### 1. Capacité d'Accueil
| Champ | Type | Description |
|-------|------|-------------|
| lit_hospi_complete | FLOAT | Nombre de lits en hospitalisation complète |
| place_hospi_partielle | FLOAT | Nombre de places en hospitalisation partielle |
| passage_urgence | FLOAT | Nombre de passages aux urgences |

#### 2. Activité Hospitalière
| Champ | Type | Description |
|-------|------|-------------|
| sejour_hospi_complete | FLOAT | Nombre de séjours en hospitalisation complète |
| sejour_hospi_partielle | FLOAT | Nombre de séjours en hospitalisation partielle |
| journee_hospi_complete | FLOAT | Nombre de journées d'hospitalisation complète |

#### 3. Taux d'Occupation
| Champ | Type | Description |
|-------|------|-------------|
| taux_occupation | FLOAT | Taux d'occupation global |
| taux_occupation1 | FLOAT | Taux d'occupation alternatif |

#### 4. Évolutions des Capacités
| Champ | Type | Description |
|-------|------|-------------|
| evolution_lit_hospi_complete | FLOAT | Variation du nombre de lits (vs année précédente) |
| evolution_percent_lit_hospi_complete | FLOAT | Variation en % du nombre de lits |
| evolution_place_hospi_partielle | FLOAT | Variation des places en hospitalisation partielle |
| evolution_percent_place_hospi_partielle | FLOAT | Variation en % des places partielles |

#### 5. Évolutions de l'Activité
| Champ | Type | Description |
|-------|------|-------------|
| evolution_sejour_hospi_complete | FLOAT | Variation des séjours complets |
| evolution_sejour_hospi_partielle | FLOAT | Variation des séjours partiels |
| evolution_journee_hospi_complete | FLOAT | Variation des journées d'hospitalisation |
| evolution_passage_urgence | FLOAT | Variation des passages aux urgences |
| evolution_percent_passage_urgence | FLOAT | Variation en % des passages aux urgences |

#### 6. Évolutions des Taux
| Champ | Type | Description |
|-------|------|-------------|
| evolution_taux_occupation1 | FLOAT | Variation du taux d'occupation |
| evolution_percent_taux_occupation1 | FLOAT | Variation en % du taux d'occupation |

#### 7. Données Démographiques et Indicateurs
| Champ | Type | Description |
|-------|------|-------------|
| population | FLOAT | Population de référence |
| tx_brut_tt_age_pour_mille | FLOAT | Taux brut pour 1000 habitants |
| tx_standard_tt_age_pour_mille | FLOAT | Taux standardisé pour 1000 habitants |
| indice_comparatif_tt_age_percent | FLOAT | Indice comparatif tous âges (%) |

Cette table fournit une vue complète des capacités hospitalières et de leur utilisation, incluant :
- Les capacités d'accueil en hospitalisation complète et partielle
- L'activité détaillée (séjours, journées, passages aux urgences)
- Les taux d'occupation et leurs évolutions
- Les variations annuelles de tous les indicateurs
- Les données démographiques et indicateurs standardisés

Les données sont disponibles par :
- Service médical (classification)
- Niveau administratif (région/département)
- Année
- Type d'hospitalisation (complète/partielle)

## Vue Globale (Page Principale)

### 1. Structure des Données

#### a. Sources de Données
```python
# Dataset principal
query_main = """
    SELECT * FROM `projet-jbn-data-le-wagon.dbt_medical_analysis_join_total_morbidite.class_join_total_morbidite_sexe_population`
"""

# Données de capacité
query_capacite = """
    SELECT * FROM `projet-jbn-data-le-wagon.dbt_medical_analysis_join_total_morbidite_capacite.class_join_total_morbidite_capacite_kpi`
"""
```

#### b. DataFrames Spécialisés
1. **df_nbr_hospi** : Données d'hospitalisation
   ```python
   df_nbr_hospi = df_complet[[
       'niveau', 'year', 'region', 'nom_region', 'pathologie', 'nom_pathologie', 'sexe',
       'nbr_hospi', 'evolution_nbr_hospi', 'evolution_percent_nbr_hospi',
       'evolution_hospi_total_24h', 'evolution_hospi_total_jj', 'indice_comparatif_tt_age_percent',
       'tranche_age_0_1', ..., 'tranche_age_85_et_plus', 'classification'
   ]]
   ```

2. **df_duree_hospi** : Durées de séjour
   ```python
   df_duree_hospi = df_complet[[
       'niveau', 'year', 'region', 'nom_pathologie', 'sexe',
       'AVG_duree_hospi', 'evolution_AVG_duree_hospi', 'evolution_percent_AVG_duree_hospi',
       'evolution_hospi_total_jj', 'classification'
   ]]
   ```

3. **df_tranche_age_hospi** : Analyses par âge
   ```python
   df_tranche_age_hospi = df_complet[[
       'niveau', 'year', 'region', 'nom_pathologie',
       'tranche_age_0_1', ..., 'tranche_age_85_et_plus',
       'tx_brut_tt_age_pour_mille', 'tx_standard_tt_age_pour_mille',
       'indice_comparatif_tt_age_percent', 'classification'
   ]]
   ```

### 2. Interface et Fonctionnalités

#### a. Chargement des Données
```python
@st.cache_resource
def fetch_data():
    # Chargement avec gestion d'erreurs et cache
    # Conversion des dates
    df_complet['year'] = pd.to_datetime(df_complet['year'])
```

#### b. Métriques Principales
```python
@st.cache_data
def calculate_main_metrics(df_nbr_hospi, df_capacite_hospi, selected_sex='Ensemble'):
    metrics = {}
    # Calcul des hospitalisations par année
    # Calcul des lits disponibles par année
    return metrics
```

### 3. Structure des Onglets

#### a. Évolution des Hospitalisations (Tab 1)
- Métriques clés 2018-2022
- Graphiques d'évolution
- Analyses comparatives

#### b. Analyse Géographique (Tab 2)
- Cartes interactives
- Répartition régionale
- Comparaisons territoriales

#### c. Analyse par Pathologie (Tab 3)
- Sélecteur de pathologies
- Graphiques combinés
- Visualisations 3D temporelles

#### d. Profil Démographique (Tab 4)
- Distribution par âge
- Évolution des taux
- Heatmaps démographiques

#### e. Performance des Services (Tab 5)
- Comparaison des services
- Analyses temporelles
- Indicateurs de performance

### 4. Visualisations Spécifiques

#### a. Graphiques Temporels
```python
# Graphique combiné hospitalisations/durée
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(
    go.Bar(x=hospi_by_pathology['nom_pathologie'], y=hospi_by_pathology['nbr_hospi']),
    secondary_y=False
)
```

#### b. Graphiques 3D et Animations
```python
# Animation temporelle
fig = px.scatter(
    combined_data,
    x='nbr_hospi',
    y='AVG_duree_hospi',
    animation_frame='year',
    size='nbr_hospi',
    color='AVG_duree_hospi'
)
```

#### c. Heatmaps Démographiques
```python
fig_heatmap = px.density_heatmap(
    df_age_service_melted,
    x='tranche_age',
    y='classification',
    z='value',
    title='Distribution des hospitalisations par âge et service'
)
```

### 5. Optimisations et Performance

#### a. Mise en Cache
- Utilisation de `@st.cache_resource` pour les données
- Utilisation de `@st.cache_data` pour les calculs

#### b. Interface de Chargement
```python
def load_with_progress():
    # Interface visuelle de chargement
    # Barre de progression
    # Gestion des erreurs
```

#### c. Gestion de la Mémoire
- Création de vues spécifiques
- Filtrage optimal des données
- Nettoyage des données non utilisées

## Relations et Utilisation des Tables

#### 1. Jointures et Relations
Les tables `class_join_total_morbidite_sexe_population` et `class_join_total_morbidite_capacite_kpi` sont liées par les champs suivants :
- `niveau` (Départements/Régions)
- `year` (Année)
- `classification` (Type de service médical)
- `region`/`code_region` (Identifiant territorial)

#### 2. Complémentarité des Données
| Table Population | Table Capacité | Utilisation Combinée |
|-----------------|----------------|---------------------|
| Nombre d'hospitalisations | Nombre de lits | Taux d'occupation |
| Durée moyenne de séjour | Journées d'hospitalisation | Efficacité des services |
| Données démographiques | Capacité d'accueil | Adéquation ressources/besoins |

#### 3. Cas d'Utilisation dans l'Application

##### a. Vue Globale
```python
# Exemple de jointure pour l'analyse globale
df_analyse = pd.merge(
    df_population,
    df_capacite,
    on=['niveau', 'year', 'classification', 'region'],
    how='left'
)

# Calcul des indicateurs combinés
df_analyse['taux_occupation'] = (df_analyse['hospi_total_jj'] / 
                               (df_analyse['lit_hospi_complete'] * 365)) * 100
```

##### b. Analyse Géographique
```python
# Analyse territoriale des capacités et besoins
analyse_territoriale = df_analyse.groupby(['region', 'classification']).agg({
    'nbr_hospi': 'sum',
    'lit_hospi_complete': 'sum',
    'taux_occupation': 'mean',
    'population': 'first'
}).reset_index()
```

##### c. Focus par Service
```python
# Analyse spécifique par service médical
def analyse_service(classification, annee):
    return df_analyse[
        (df_analyse['classification'] == classification) & 
        (df_analyse['year'] == annee)
    ].agg({
        'nbr_hospi': 'sum',
        'lit_hospi_complete': 'sum',
        'AVG_duree_hospi': 'mean',
        'taux_occupation': 'mean'
    })
```

#### 4. Indicateurs Dérivés

| Indicateur | Calcul | Description |
|------------|--------|-------------|
| Taux d'occupation | `hospi_total_jj / (lit_hospi_complete * 365)` | Utilisation des capacités |
| Rotation des lits | `nbr_hospi / lit_hospi_complete` | Efficacité d'utilisation |
| Durée moyenne effective | `journee_hospi_complete / sejour_hospi_complete` | Durée réelle des séjours |

#### 5. Exemples de Visualisations Combinées

##### a. Carte de France
```python
# Préparation des données pour la carte
map_data = df_analyse.groupby('region').agg({
    'nbr_hospi': 'sum',
    'lit_hospi_complete': 'sum',
    'taux_occupation': 'mean'
}).reset_index()
```

##### b. Graphiques d'Évolution
```python
# Évolution temporelle des capacités et besoins
evolution_data = df_analyse.groupby('year').agg({
    'nbr_hospi': 'sum',
    'lit_hospi_complete': 'sum',
    'taux_occupation': 'mean'
}).reset_index()
```

#### 6. Considérations Importantes

1. **Gestion des Données Manquantes**
   ```python
   # Remplacement des valeurs manquantes
   df_analyse['taux_occupation'] = df_analyse['taux_occupation'].fillna(
       df_analyse.groupby('classification')['taux_occupation'].transform('mean')
   )
   ```

2. **Cohérence Temporelle**
   ```python
   # Vérification de la cohérence des données
   def verifier_coherence(df):
       return df.groupby('year').agg({
           'nbr_hospi': 'sum',
           'sejour_hospi_complete': 'sum'
       }).eval('difference = nbr_hospi - sejour_hospi_complete')
   ```

3. **Agrégations Territoriales**
   ```python
   # Agrégation région -> département
   def agreger_territoire(df, niveau_cible):
       colonnes_somme = ['nbr_hospi', 'lit_hospi_complete', 'journee_hospi_complete']
       colonnes_moyenne = ['AVG_duree_hospi', 'taux_occupation']
       
       return df.groupby(['year', niveau_cible]).agg({
           **{col: 'sum' for col in colonnes_somme},
           **{col: 'mean' for col in colonnes_moyenne}
       })
   ```

## Vue Globale
- Tableaux de bord interactifs avec filtres par année et région
- Graphiques de tendances temporelles
- Cartes de France pour visualisation géographique

### Focus Chirurgie (Détaillé)

#### 1. Filtres Globaux
- **Sélection du sexe** : "Ensemble", "Homme", "Femme"
- **Sélection de l'année** : Toutes les années ou année spécifique
- **Filtrage des données** :
  ```python
  df_filtered = df.copy()
  if selected_sex != "Ensemble":
      df_filtered = df_filtered[df_filtered['sexe'] == selected_sex]
  if selected_year != "Toutes les années":
      df_filtered = df_filtered[df_filtered['annee'] == int(selected_year)]
  ```

#### 2. Analyse par Pathologies (Tab 1)

##### a. Métriques Principales
- **Total d'hospitalisations** : Somme de `nbr_hospi`
- **Durée moyenne** : Moyenne de `AVG_duree_hospi`
- **Indice comparatif** : Moyenne de `indice_comparatif_tt_age_percent`
- **Hospitalisations < 24h** : Pourcentage calculé à partir de `hospi_total_24h`
- **Tranche d'âge majoritaire** : Analyse des colonnes `tranche_age_*`

##### b. Graphique Principal : Hospitalisations et Durée de Séjour
- **Type** : Graphique combiné (Barres + Ligne)
- **Données** :
  ```python
  hospi_by_pathology = df_filtered.groupby('nom_pathologie').agg({
      'nbr_hospi': 'sum',
      'AVG_duree_hospi': 'mean'
  })
  ```
- **Visualisation** :
  - Barres : Nombre d'hospitalisations par pathologie
  - Ligne : Durée moyenne de séjour
  - Filtrage : Top N pathologies (configurable via slider)

##### c. Graphique Dynamique : Scatter Plot Animé
- **Type** : Scatter plot avec animation temporelle
- **Données** :
  ```python
  combined_data = pd.merge(
      df_nbr_hospi.groupby(['nom_pathologie', 'annee'])['nbr_hospi'].sum(),
      df_duree_hospi.groupby(['nom_pathologie', 'annee'])['AVG_duree_hospi'].mean(),
      on=['nom_pathologie', 'annee']
  )
  ```
- **Caractéristiques** :
  - Taille des bulles : Nombre d'hospitalisations
  - Couleur : Durée moyenne de séjour
  - Animation : Par année
  - Texte : Nom de la pathologie

#### 3. Analyse par Capacité (Tab 2)
- Visualisations géographiques des capacités
- Analyse des ressources par région
- Évolution temporelle des capacités

#### 4. Analyse Démographique (Tab 3)
- Distribution par âge
- Analyses des taux standardisés
- Comparaisons démographiques régionales

#### 5. Caractéristiques Techniques

- **Thème de couleurs** :
  ```python
  MAIN_COLOR = '#003366'  # Bleu marine principal
  SECONDARY_COLOR = '#AFDC8F'  # Vert clair complémentaire
  ACCENT_COLOR = '#3D7317'  # Vert foncé pour les accents
  ```
- **Mise en page** : Utilisation de colonnes Streamlit pour une disposition responsive

### Focus Obstétrique (Détaillé)

#### 1. Source de Données
```python
query = """
    SELECT *
    FROM `projet-jbn-data-le-wagon.dbt_medical_analysis_join_total_morbidite.class_join_total_morbidite_sexe_population`
    WHERE classification = 'O' AND niveau = 'Régions'
"""
```

#### 2. Filtres Globaux
- Identiques à la chirurgie avec des clés spécifiques :
  ```python
  selected_sex = st.selectbox("Sexe", ["Ensemble", "Homme", "Femme"], key="selecteur_sexe")
  selected_year = st.selectbox("Année", years_options, key="year_filter")
  ```

#### 3. Analyse par Pathologies (Tab 1)

##### a. Métriques Clés
- **Total d'hospitalisations** : 
  ```python
  total_hospi = path_data['nbr_hospi'].sum()
  st.metric("Total d'hospitalisations", f"{total_hospi/1_000:,.2f}K")
  ```
- **Durée moyenne de séjour** :
  ```python
  avg_duration = df_filtered['AVG_duree_hospi'].mean()
  st.metric("Durée moyenne", f"{avg_duration:.1f} jours")
  ```
- **Indice comparatif** : Moyenne de `indice_comparatif_tt_age_percent`
- **Hospitalisations < 24h** : Pourcentage calculé à partir de `hospi_total_24h`
- **Analyse par âge** : Utilisation des colonnes `tranche_age_*`

##### b. Visualisations Principales
1. **Graphique Combiné Hospitalisations/Durée**
   - Type : Subplot avec axe Y secondaire
   - Données : Agrégation par pathologie
   - Composants :
     - Barres : Nombre d'hospitalisations
     - Ligne : Durée moyenne de séjour
   - Interactivité : Hover templates personnalisés

2. **Scatter Plot Dynamique**
   - Animation temporelle par année
   - Taille des bulles proportionnelle au nombre d'hospitalisations
   - Échelle de couleur Viridis pour la durée de séjour

#### 4. Spécificités Obstétriques
- Focus sur les pathologies liées à la grossesse et l'accouchement
- Analyse des durées de séjour typiques en obstétrique
- Suivi des tendances par tranche d'âge

#### 5. Différences avec la Chirurgie
- Classification 'O' spécifique à l'obstétrique
- Métriques adaptées aux séjours obstétriques
- Focus sur les pathologies médicales chroniques
- Analyse des durées de séjour plus longues

#### 6. Visualisations Spécifiques
- **Graphiques Temporels** :
  ```python
  combined_data_3d = pd.merge(
      df_nbr_hospi.groupby(['nom_pathologie', 'annee'])['nbr_hospi'].sum(),
      df_duree_hospi.groupby(['nom_pathologie', 'annee'])['AVG_duree_hospi'].mean(),
      on=['nom_pathologie', 'annee']
  )
  ```
- **Personnalisation des Graphiques** :
  - Utilisation de templates Plotly White
  - Interactivité avancée
  - Animations fluides pour les tendances temporelles

### Focus Médecine (Détaillé)

#### 1. Source de Données et Spécificités
```python
query = """
    SELECT *
    FROM `projet-jbn-data-le-wagon.dbt_medical_analysis_join_total_morbidite.class_join_total_morbidite_sexe_population`
    WHERE classification = 'M' AND niveau = 'Régions'
"""
```

#### 2. Prétraitement des Données
- **Gestion des Données COVID** :
  ```python
  mask_covid = (df['nom_pathologie'] == 'Infection à coronavirus (COVID-19)') & 
               (df['annee'].isin([2018, 2019]))
  df.loc[mask_covid, ['nbr_hospi', 'AVG_duree_hospi', 'indice_comparatif_tt_age_percent']] = 0
  ```

#### 3. Structure des Onglets
1. **Analyse par pathologies** (📈)
   - Sélecteur de pathologies avec option "Toutes les pathologies"
   - Métriques clés affichées en colonnes
   - Visualisations combinées

2. **Analyse par capacité** (🗺️)
   - Visualisations géographiques
   - Analyse des capacités hospitalières

3. **Analyse démographique** (🏥)
   - Distribution par âge
   - Analyses comparatives

#### 4. Métriques Spécifiques à la Médecine
- **Indicateurs de Performance** :
   ```python
   total_hospi = path_data['nbr_hospi'].sum()
   avg_duration = df_filtered['AVG_duree_hospi'].mean()
   indice_comparatif = path_data['indice_comparatif_tt_age_percent'].mean()
   ```

3. **Visualisations Spécifiques Médecine**
   - **Graphique Principal** :
     - Barres : Nombre d'hospitalisations par pathologie
     - Ligne : Durée moyenne de séjour
   - **Scatter Plot Dynamique** :
     - Animation temporelle
     - Taille des bulles : Nombre d'hospitalisations
     - Couleur : Durée de séjour

##### b. Analyse par Capacité (Tab 2)
- Répartition géographique des capacités médicales
- Analyse des ressources par région
- Évolution temporelle des capacités

##### c. Analyse Démographique (Tab 3)
- Distribution par âge des patients médicaux
- Tendances démographiques spécifiques
- Comparaisons régionales

#### 5. Spécificités de la Médecine
- **Classification** : Utilisation du code 'M'
- **Durées de Séjour** : Généralement plus longues que les autres services
- **Population** : Souvent âgée ou en réadaptation

#### 6. Visualisations Spécifiques
- **Graphiques Temporels** :
  ```python
  combined_data_3d = pd.merge(
      df_nbr_hospi.groupby(['nom_pathologie', 'annee'])['nbr_hospi'].sum(),
      df_duree_hospi.groupby(['nom_pathologie', 'annee'])['AVG_duree_hospi'].mean(),
      on=['nom_pathologie', 'annee']
  )
  ```
- **Personnalisation des Graphiques** :
  - Utilisation de templates Plotly White
  - Interactivité avancée
  - Animations fluides pour les tendances temporelles

### Focus Psychiatrie (Détaillé)

#### 1. Source de Données
```python
query = """
    SELECT *
    FROM `projet-jbn-data-le-wagon.dbt_medical_analysis_join_total_morbidite.class_join_total_morbidite_sexe_population`
    WHERE classification = 'PSY' AND niveau = 'Régions'
"""
```

#### 2. Prétraitement des Données
- **Gestion des Données COVID** :
  ```python
  mask_covid = (df['nom_pathologie'] == 'Infection à coronavirus (COVID-19)') & 
               (df['annee'].isin([2018, 2019]))
  df.loc[mask_covid, ['nbr_hospi', 'AVG_duree_hospi', 'indice_comparatif_tt_age_percent']] = 0
  ```

#### 3. Filtres et Interface
- **Filtres Principaux** :
  ```python
  selected_sex = st.selectbox("Sexe", ["Ensemble", "Homme", "Femme"], key="selecteur_sexe_psy")
  selected_year = st.selectbox("Année", years_options, key="year_filter_psy")
  ```

#### 4. Structure de l'Analyse

##### a. Analyse par Pathologies (Tab 1)
1. **Sélection des Pathologies**
   - Liste déroulante complète des pathologies psychiatriques
   - Option "Toutes les pathologies" incluse

2. **Métriques Clés**
   ```python
   total_hospi = path_data['nbr_hospi'].sum()
   avg_duration = df_filtered['AVG_duree_hospi'].mean()
   indice_comparatif = path_data['indice_comparatif_tt_age_percent'].mean()
   ```

3. **Visualisations Spécifiques Psychiatrie**
   - **Graphique Principal** :
     - Barres : Nombre d'hospitalisations par pathologie
     - Ligne : Durée moyenne de séjour
   - **Scatter Plot Dynamique** :
     - Animation temporelle
     - Taille des bulles : Nombre d'hospitalisations
     - Couleur : Durée de séjour

##### b. Analyse par Capacité (Tab 2)
- Visualisations géographiques des capacités psychiatriques
- Analyse des ressources par région
- Évolution temporelle des capacités

##### c. Analyse Démographique (Tab 3)
- Distribution par âge des patients psychiatriques
- Tendances démographiques spécifiques
- Comparaisons régionales

#### 5. Spécificités de la Psychiatrie
- **Classification** : Code 'PSY' spécifique
- **Durées de Séjour** : Typiquement plus longues
- **Population** : Souvent âgée ou en réadaptation

#### 6. Visualisations Spécifiques
- **Graphiques Temporels** :
  ```python
  combined_data_3d = pd.merge(
      df_nbr_hospi.groupby(['nom_pathologie', 'annee'])['nbr_hospi'].sum(),
      df_duree_hospi.groupby(['nom_pathologie', 'annee'])['AVG_duree_hospi'].mean(),
      on=['nom_pathologie', 'annee']
  )
  ```
- **Personnalisation** :
  - Templates adaptés aux longues durées
  - Échelles ajustées aux séjours prolongés
  - Visualisations des progressions

#### 7. Points Clés Psychiatrie
- Focus sur la réadaptation et la récupération
- Suivi des durées de séjour prolongées
- Analyse des parcours de soins
- Évaluation des résultats de réadaptation

### Focus SSR (Soins de Suite et Réadaptation) (Détaillé)

#### 1. Source de Données
```python
query = """
    SELECT *
    FROM `projet-jbn-data-le-wagon.dbt_medical_analysis_join_total_morbidite.class_join_total_morbidite_sexe_population`
    WHERE classification = 'SSR' AND niveau = 'Régions'
"""
```

#### 2. Interface et Filtres
- **Sélecteurs Principaux** :
  ```python
  selected_sex = st.selectbox("Sexe", ["Ensemble", "Homme", "Femme"], key="selecteur_sexe_ssr")
  selected_year = st.selectbox("Année", years_options, key="year_filter_ssr")
  ```

#### 3. Structure de l'Analyse

##### a. Analyse par Pathologies (Tab 1)
1. **Sélection des Pathologies**
   - Liste déroulante complète des pathologies SSR
   - Option "Toutes les pathologies" incluse

2. **Métriques Clés**
   ```python
   total_hospi = path_data['nbr_hospi'].sum()
   avg_duration = df_filtered['AVG_duree_hospi'].mean()
   indice_comparatif = path_data['indice_comparatif_tt_age_percent'].mean()
   ```

3. **Visualisations Spécifiques SSR**
   - **Graphique Principal** :
     - Barres : Nombre d'hospitalisations par pathologie
     - Ligne : Durée moyenne de séjour
   - **Scatter Plot Dynamique** :
     - Animation temporelle
     - Taille des bulles : Nombre d'hospitalisations
     - Couleur : Durée de séjour

##### b. Analyse par Capacité (Tab 2)
- Répartition géographique des capacités SSR
- Analyse des ressources par région
- Évolution temporelle des capacités

##### c. Analyse Démographique (Tab 3)
- Distribution par âge des patients SSR
- Tendances démographiques spécifiques
- Comparaisons régionales

#### 4. Spécificités SSR

##### a. Caractéristiques Uniques
- **Classification** : Utilisation du code 'SSR'
- **Durées de Séjour** : Typiquement plus longues
- **Population** : Souvent âgée ou en réadaptation

##### b. Traitement des Données
```python
# Préparation des données pour visualisation
df_filtered = df.copy()
if selected_sex != "Ensemble":
    df_filtered = df_filtered[df_filtered['sexe'] == selected_sex]
if selected_year != "Toutes les années":
    df_filtered = df_filtered[df_filtered['annee'] == int(selected_year)]
```

##### c. Visualisations Adaptées
- **Graphiques Temporels** :
  ```python
  combined_data_3d = pd.merge(
      df_nbr_hospi.groupby(['nom_pathologie', 'annee'])['nbr_hospi'].sum(),
      df_duree_hospi.groupby(['nom_pathologie', 'annee'])['AVG_duree_hospi'].mean(),
      on=['nom_pathologie', 'annee']
  )
  ```
- **Personnalisation** :
  - Templates adaptés aux longues durées
  - Échelles ajustées aux séjours prolongés
  - Visualisations des progressions

#### 5. Points Clés SSR
- Focus sur la réadaptation et la récupération
- Suivi des durées de séjour prolongées
- Analyse des parcours de soins
- Évaluation des résultats de réadaptation

## Outils de Visualisation Utilisés

### Bibliothèques
- **Plotly Express** : Graphiques interactifs
- **Plotly Graph Objects** : Visualisations personnalisées
- **Streamlit** : Interface utilisateur et widgets

### Types de Graphiques
1. **Graphiques en Barres**
   - Comparaisons entre régions
   - Analyses par pathologie

2. **Courbes d'Évolution**
   - Tendances temporelles
   - Évolutions des métriques clés

3. **Cartes Choroplèthes**
   - Visualisations géographiques
   - Comparaisons régionales

4. **Graphiques en Boîte**
   - Distribution des durées de séjour
   - Analyses statistiques

## Générateur de Graphiques Personnalisés
- Interface interactive pour création de visualisations
- Sélection flexible des métriques
- Filtres dynamiques (année, région, pathologie)
- Export des visualisations
