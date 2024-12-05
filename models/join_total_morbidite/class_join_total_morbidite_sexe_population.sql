WITH mega_join AS (
    SELECT 
        t1.niveau
        ,t1.cle_unique
        ,t1.sexe
        ,t1.year
        ,t1.annee
        ,t1.pathologie
        ,t1.code_pathologie
        ,t1.nom_pathologie
        ,t1.region
        ,t1.code_region
        ,t1.nom_region
        ,t1.nbr_hospi
        ,t1.evolution_nbr_hospi1 as evolution_nbr_hospi
        ,t1.evolution_percent_nbr_hospi1 as evolution_percent_nbr_hospi
        
        ,t2.hospi_prog_24h
        ,t2.hospi_autres_24h
        ,t2.hospi_total_24h
        ,t2.hospi_1J
        ,t2.hospi_2J
        ,t2.hospi_3J
        ,t2.hospi_4J
        ,t2.hospi_5J
        ,t2.hospi_6J
        ,t2.hospi_7J
        ,t2.hospi_8J
        ,t2.hospi_9J
        ,t2.hospi_10J_19J
        ,t2.hospi_20J_29J
        ,t2.hospi_30J
        ,t2.hospi_total_jj
        ,t2.total_hospi
        ,t2.AVG_duree_hospi
        ,t2.evolution_hospi_total_24h1 as evolution_hospi_total_24h
        ,t2.evolution_percent_hospi_total_24h1 as evolution_percent_hospi_total_24h
        ,t2.evolution_hospi_total_jj1 as evolution_hospi_total_jj
        ,t2.evolution_percent_hospi_total_jj1 as evolution_percent_hospi_total_jj
        ,t2.evolution_total_hospi2 as evolution_total_hospi
        ,t2.evolution_percent_total_hospi2 as evolution_percent_total_hospi
        ,t2.evolution_AVG_duree_hospi1 as evolution_AVG_duree_hospi
        ,t2.evolution_percent_AVG_duree_hospi1 as evolution_percent_AVG_duree_hospi

        ,t3.tranche_age_0_1
        ,t3.tranche_age_1_4
        ,t3.tranche_age_5_14
        ,t3.tranche_age_15_24
        ,t3.tranche_age_25_34
        ,t3.tranche_age_35_44
        ,t3.tranche_age_45_54
        ,t3.tranche_age_55_64
        ,t3.tranche_age_65_74
        ,t3.tranche_age_75_84
        ,t3.tranche_age_85_et_plus
        ,t3.tx_brut_tt_age_pour_mille
        ,t3.tx_standard_tt_age_pour_mille
        ,t3.indice_comparatif_tt_age_percent
        ,t3.evolution_tx_brut_tt_age_pour_mille1 as evolution_tx_brut_tt_age_pour_mille
        ,t3.evolution_percent_tx_brut_tt_age_pour_mille1 as evolution_percent_tx_brut_tt_age_pour_mille
        ,t3.evolution_tx_standard_tt_age_pour_mille2 as evolution_tx_standard_tt_age_pour_mille
        ,t3.evolution_percent_tx_standard_tt_age_pour_mille2 as evolution_percent_tx_standard_tt_age_pour_mille
        ,t3.evolution_indice_comparatif_tt_age_percent1 as evolution_indice_comparatif_tt_age_percent
        ,t3.evolution_percent_indice_comparatif_tt_age_percent1 as evolution_percent_indice_comparatif_tt_age_percent

    FROM 
        {{ref("mart_nbr_hospi_total_evol")}} t1
    LEFT JOIN 
        {{ref("mart_duree_sejours_total_evol")}} t2
        ON t1.cle_unique = t2.cle_unique
    INNER JOIN 
        {{ref("mart_taux_recours_total_evol")}} t3 
        ON t1.cle_unique = t3.cle_unique
        AND t1.sexe = t3.sexe
    WHERE 
        t1.tranche_age = 'Tous âges confondus'
), 
mega_join_class as (
SELECT 
    t1.* 
    ,classification
FROM mega_join AS t1
LEFT JOIN {{ref("stg_morbidite_h__class_services")}} c2
ON t1.nom_pathologie = c2.pathologie
ORDER BY cle_unique
),
join_dpt AS (
    SELECT
        t1.*,
        t2.population AS population
    FROM mega_join_class t1
    LEFT JOIN {{ ref("stg_pop_departement__population_departement") }} t2
        ON t1.annee = t2.annee
        AND t1.nom_region = t2.nom_departement
    WHERE t1.niveau = 'Départements'  
),    
join_reg AS (
    SELECT
        t1.*,
        t2.population AS population
    FROM mega_join_class t1
    LEFT JOIN {{ ref("stg_pop_departement__population_region") }} t2
        ON t1.annee = t2.annee
        AND t1.nom_region = t2.region
    WHERE t1.niveau = 'Régions'
)

SELECT *
FROM join_dpt
UNION ALL
SELECT *
FROM join_reg

