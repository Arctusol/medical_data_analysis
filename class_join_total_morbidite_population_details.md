Identification et localisation

    niveau (object) : Niveau administratif (département, région).
    cle_unique (object) : Identifiant unique par enregistrement.
    sexe (object) : Sexe (Homme/Femme/Ensemble).
    year (dbdate) : Date en format AAAA-MM-JJ.
    annee (Int64) : Année (format numérique).
    region (object) : Code ou nom de la région.
    code_region (Int64) : Code numérique de la région.
    nom_region (object) : Nom complet de la région.

Pathologie

    pathologie (object) : Code descriptif de la pathologie.
    code_pathologie (Int64) : Code numérique de la pathologie.
    nom_pathologie (object) : Nom complet de la pathologie.

Hospitalisations

    nbr_hospi (Int64) : Nombre total d’hospitalisations.
    evolution_nbr_hospi (Int64) : Variation absolue du nombre d’hospitalisations.
    evolution_percent_nbr_hospi (float64) : Variation en pourcentage.
    hospi_prog_24h (Int64) : Hospitalisations programmées (24h).
    hospi_autres_24h (Int64) : Autres hospitalisations (24h).
    hospi_total_24h (Int64) : Total hospitalisations en 24h.
    18-29. hospi_1J à hospi_30J (Int64) : Durées d’hospitalisation (jours spécifiques ou plages).
    hospi_total_jj (Int64) : Total hospitalisations, toutes durées confondues.
    total_hospi (Int64) : Nombre global d’hospitalisations.
    AVG_duree_hospi (float64) : Durée moyenne des hospitalisations.

Évolution hospitalière

33-39. evolution_hospi_* (Int64, float64) : Variations absolues et en pourcentage des différents indicateurs hospitaliers (24h, total, durée moyenne, etc.).
Tranches d’âge

40-50. tranche_age_* (float64) : Proportions d’hospitalisations par tranche d’âge (de 0-1 an à 85 ans et plus).

Taux et indices

    tx_brut_tt_age_pour_mille (float64) : Taux brut pour 1 000 habitants.
    tx_standard_tt_age_pour_mille (float64) : Taux standardisé pour 1 000 habitants.
    indice_comparatif_tt_age_percent (float64) : Indice standardisé en pourcentage.
    54-59. evolution_tx_* (float64) : Variations de taux brut, standardisé, et indices comparatifs en pourcentage.

Divers

    classification (object) : Classification en terme de service médical : M (Médecine), C (Chirurgie), SSR (soins de suite et de réadaptation), O (Obstétrique), ESND (Établissement de soin longue durée), PSY (Psychothérapie).
    population (Int64) : Population totale associée par région et département (valeurs dupliqués).

Vérification manquante

    evolution_percent_indice_comparatif_tt_age_percent (float64) : Variation en pourcentage de l'indice comparatif pour tous âges.