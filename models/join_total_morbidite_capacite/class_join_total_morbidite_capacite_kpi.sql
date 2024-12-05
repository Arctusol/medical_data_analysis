WITH nullval as (
SELECT 
    niveau,
    cle_unique,
    sexe,
    year,
    annee,
    region,
    code_region,
    nom_region,
    classification,
    IFNULL(CAST(nbr_hospi AS FLOAT64), 0) AS nbr_hospi,
    IFNULL(CAST(evolution_nbr_hospi AS FLOAT64), 0) AS evolution_nbr_hospi,
    IFNULL(CAST(evolution_percent_nbr_hospi AS FLOAT64), 0) AS evolution_percent_nbr_hospi,
    IFNULL(CAST(hospi_prog_24h AS FLOAT64), 0) AS hospi_prog_24h,
    IFNULL(CAST(hospi_autres_24h AS FLOAT64), 0) AS hospi_autres_24h,
    IFNULL(CAST(hospi_total_24h AS FLOAT64), 0) AS hospi_total_24h,
    IFNULL(CAST(hospi_1J AS FLOAT64), 0) AS hospi_1J,
    IFNULL(CAST(hospi_2J AS FLOAT64), 0) AS hospi_2J,
    IFNULL(CAST(hospi_3J AS FLOAT64), 0) AS hospi_3J,
    IFNULL(CAST(hospi_4J AS FLOAT64), 0) AS hospi_4J,
    IFNULL(CAST(hospi_5J AS FLOAT64), 0) AS hospi_5J,
    IFNULL(CAST(hospi_6J AS FLOAT64), 0) AS hospi_6J,
    IFNULL(CAST(hospi_7J AS FLOAT64), 0) AS hospi_7J,
    IFNULL(CAST(hospi_8J AS FLOAT64), 0) AS hospi_8J,
    IFNULL(CAST(hospi_9J AS FLOAT64), 0) AS hospi_9J,
    IFNULL(CAST(hospi_10J_19J AS FLOAT64), 0) AS hospi_10J_19J,
    IFNULL(CAST(hospi_20J_29J AS FLOAT64), 0) AS hospi_20J_29J,
    IFNULL(CAST(hospi_30J AS FLOAT64), 0) AS hospi_30J,
    IFNULL(CAST(hospi_total_jj AS FLOAT64), 0) AS hospi_total_jj,
    IFNULL(CAST(total_hospi AS FLOAT64), 0) AS total_hospi,
    IFNULL(CAST(AVG_duree_hospi AS FLOAT64), 0) AS AVG_duree_hospi,
    IFNULL(CAST(evolution_hospi_total_24h AS FLOAT64), 0) AS evolution_hospi_total_24h,
    IFNULL(CAST(evolution_percent_hospi_total_24h AS FLOAT64), 0) AS evolution_percent_hospi_total_24h,
    IFNULL(CAST(evolution_hospi_total_jj AS FLOAT64), 0) AS evolution_hospi_total_jj,
    IFNULL(CAST(evolution_percent_hospi_total_jj AS FLOAT64), 0) AS evolution_percent_hospi_total_jj,
    IFNULL(CAST(evolution_total_hospi AS FLOAT64), 0) AS evolution_total_hospi,
    IFNULL(CAST(evolution_percent_total_hospi AS FLOAT64), 0) AS evolution_percent_total_hospi,
    IFNULL(CAST(evolution_AVG_duree_hospi AS FLOAT64), 0) AS evolution_AVG_duree_hospi,
    IFNULL(CAST(evolution_percent_AVG_duree_hospi AS FLOAT64), 0) AS evolution_percent_AVG_duree_hospi,
    IFNULL(CAST(tranche_age_0_1 AS FLOAT64), 0) AS tranche_age_0_1,
    IFNULL(CAST(tranche_age_1_4 AS FLOAT64), 0) AS tranche_age_1_4,
    IFNULL(CAST(tranche_age_5_14 AS FLOAT64), 0) AS tranche_age_5_14,
    IFNULL(CAST(tranche_age_15_24 AS FLOAT64), 0) AS tranche_age_15_24,
    IFNULL(CAST(tranche_age_25_34 AS FLOAT64), 0) AS tranche_age_25_34,
    IFNULL(CAST(tranche_age_35_44 AS FLOAT64), 0) AS tranche_age_35_44,
    IFNULL(CAST(tranche_age_45_54 AS FLOAT64), 0) AS tranche_age_45_54,
    IFNULL(CAST(tranche_age_55_64 AS FLOAT64), 0) AS tranche_age_55_64,
    IFNULL(CAST(tranche_age_65_74 AS FLOAT64), 0) AS tranche_age_65_74,
    IFNULL(CAST(tranche_age_75_84 AS FLOAT64), 0) AS tranche_age_75_84,
    IFNULL(CAST(tranche_age_85_et_plus AS FLOAT64), 0) AS tranche_age_85_et_plus,
    IFNULL(CAST(tx_brut_tt_age_pour_mille AS FLOAT64), 0) AS tx_brut_tt_age_pour_mille,
    IFNULL(CAST(tx_standard_tt_age_pour_mille AS FLOAT64), 0) AS tx_standard_tt_age_pour_mille,
    IFNULL(CAST(indice_comparatif_tt_age_percent AS FLOAT64), 0) AS indice_comparatif_tt_age_percent,
    IFNULL(CAST(evolution_tx_brut_tt_age_pour_mille AS FLOAT64), 0) AS evolution_tx_brut_tt_age_pour_mille,
    IFNULL(CAST(evolution_percent_tx_brut_tt_age_pour_mille AS FLOAT64), 0) AS evolution_percent_tx_brut_tt_age_pour_mille,
    IFNULL(CAST(evolution_tx_standard_tt_age_pour_mille AS FLOAT64), 0) AS evolution_tx_standard_tt_age_pour_mille,
    IFNULL(CAST(evolution_percent_tx_standard_tt_age_pour_mille AS FLOAT64), 0) AS evolution_percent_tx_standard_tt_age_pour_mille,
    IFNULL(CAST(evolution_indice_comparatif_tt_age_percent AS FLOAT64), 0) AS evolution_indice_comparatif_tt_age_percent,
    IFNULL(CAST(evolution_percent_indice_comparatif_tt_age_percent AS FLOAT64), 0) AS evolution_percent_indice_comparatif_tt_age_percent,
    IFNULL(CAST(population AS FLOAT64), 0) AS population,
    IFNULL(CAST(lit_hospi_complete AS FLOAT64), 0) AS lit_hospi_complete,
    IFNULL(CAST(sejour_hospi_complete AS FLOAT64), 0) AS sejour_hospi_complete,
    IFNULL(CAST(journee_hospi_complete AS FLOAT64), 0) AS journee_hospi_complete,
    IFNULL(CAST(place_hospi_partielle AS FLOAT64), 0) AS place_hospi_partielle,
    IFNULL(CAST(sejour_hospi_partielle AS FLOAT64), 0) AS sejour_hospi_partielle,
    IFNULL(CAST(passage_urgence AS FLOAT64), 0) AS passage_urgence,
    IFNULL(CAST(evolution_lit_hospi_complete AS FLOAT64), 0) AS evolution_lit_hospi_complete,
    IFNULL(CAST(evolution_percent_lit_hospi_complete AS FLOAT64), 0) AS evolution_percent_lit_hospi_complete,
    IFNULL(CAST(evolution_sejour_hospi_complete AS FLOAT64), 0) AS evolution_sejour_hospi_complete,
    IFNULL(CAST(evolution_percent_sejour_hospi_complete AS FLOAT64), 0) AS evolution_percent_sejour_hospi_complete,
    IFNULL(CAST(evolution_journee_hospi_complete AS FLOAT64), 0) AS evolution_journee_hospi_complete,
    IFNULL(CAST(evolution_percent_journee_hospi_complete AS FLOAT64), 0) AS evolution_percent_journee_hospi_complete,
    IFNULL(CAST(evolution_place_hospi_partielle AS FLOAT64), 0) AS evolution_place_hospi_partielle,
    IFNULL(CAST(evolution_percent_place_hospi_partielle AS FLOAT64), 0) AS evolution_percent_place_hospi_partielle,
    IFNULL(CAST(evolution_sejour_hospi_partielle AS FLOAT64), 0) AS evolution_sejour_hospi_partielle,
    IFNULL(CAST(evolution_percent_sejour_hospi_partielle AS FLOAT64), 0) AS evolution_percent_sejour_hospi_partielle,
    IFNULL(CAST(evolution_passage_urgence AS FLOAT64), 0) AS evolution_passage_urgence,
    IFNULL(CAST(evolution_percent_passage_urgence AS FLOAT64), 0) AS evolution_percent_passage_urgence,
    
    ROUND(safe_divide((nbr_hospi * AVG_duree_hospi) , COALESCE(journee_hospi_complete,0) + COALESCE(sejour_hospi_partielle,0)), 2) AS taux_occupation,

    ROUND(
        CASE 
            WHEN COALESCE(population, 0) = 0 THEN 0 
            ELSE (lit_hospi_complete + COALESCE(place_hospi_partielle, 0)) / population * 1000
        END, 2
    ) AS taux_equipement

FROM {{ref("class_join_total_morbidite_capacite")}}
),
base_data as (
    SELECT *
    ,AVG(taux_occupation) OVER (PARTITION BY annee, region, classification) AS taux_occupation1
    ,AVG(taux_equipement) OVER (PARTITION BY annee, region, classification) AS taux_equipement1
    FROM nullval
)
    SELECT 
        bd1.*,
        round(bd1.taux_occupation1 - COALESCE(bd2.taux_occupation1, 0),2) AS evolution_taux_occupation1,
        CASE 
            WHEN COALESCE(bd2.taux_occupation1, 0) = 0 THEN NULL 
            ELSE Round(safe_divide((bd1.taux_occupation1 - bd2.taux_occupation1) , bd2.taux_occupation1), 2)  
        END AS evolution_percent_taux_occupation1,
        round(bd1.taux_equipement1 - COALESCE(bd2.taux_equipement1, 0),2) AS evolution_taux_equipement1,
        CASE 
            WHEN COALESCE(bd2.taux_equipement1, 0) = 0 THEN NULL 
            ELSE Round(safe_divide((bd1.taux_equipement1 - bd2.taux_equipement1) , bd2.taux_equipement1), 2)  
        END AS evolution_percent_taux_equipement1,
    FROM base_data bd1
    LEFT JOIN base_data bd2 
        ON bd1.region = bd2.region
        AND bd1.classification = bd2.classification
        AND bd1.annee = bd2.annee + 1


