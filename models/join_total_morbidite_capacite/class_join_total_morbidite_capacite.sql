WITH agg_class as(
    SELECT    
        niveau
        ,CONCAT(region , "_" , annee , "_" , classification) as cle_unique
        ,sexe
        ,year
        ,annee
        ,region
        ,code_region
        ,nom_region
        ,classification
        ,SUM(nbr_hospi) as nbr_hospi
        ,ROUND(AVG(evolution_nbr_hospi),2) as evolution_nbr_hospi
        ,ROUND(AVG(evolution_percent_nbr_hospi),2) as evolution_percent_nbr_hospi
        ,SUM(hospi_prog_24h) as hospi_prog_24h
        ,SUM(hospi_autres_24h) as hospi_autres_24h
        ,SUM(hospi_total_24h) as hospi_total_24h
        ,SUM(hospi_1J) as hospi_1J
        ,SUM(hospi_2J) as hospi_2J 
        ,SUM(hospi_3J) as hospi_3J
        ,SUM(hospi_4J) as hospi_4J
        ,SUM(hospi_5J) as hospi_5J
        ,SUM(hospi_6J) as hospi_6J
        ,SUM(hospi_7J) as hospi_7J
        ,SUM(hospi_8J) as hospi_8J
        ,SUM(hospi_9J) as hospi_9J
        ,SUM(hospi_10J_19J) as hospi_10J_19J
        ,SUM(hospi_20J_29J) as hospi_20J_29J
        ,SUM(hospi_30J) as hospi_30J
        ,SUM(hospi_total_jj) as hospi_total_jj
        ,SUM(total_hospi) as total_hospi
        ,ROUND(AVG(AVG_duree_hospi),2) as AVG_duree_hospi
        ,ROUND(AVG(evolution_hospi_total_24h),2) as evolution_hospi_total_24h
        ,ROUND(AVG(evolution_percent_hospi_total_24h),2) as evolution_percent_hospi_total_24h
        ,ROUND(AVG(evolution_hospi_total_jj),2) as evolution_hospi_total_jj
        ,ROUND(AVG(evolution_percent_hospi_total_jj),2) as evolution_percent_hospi_total_jj
        ,ROUND(AVG(evolution_total_hospi),2) as evolution_total_hospi
        ,ROUND(AVG(evolution_percent_total_hospi),2) as evolution_percent_total_hospi
        ,ROUND(AVG(evolution_AVG_duree_hospi),2) as evolution_AVG_duree_hospi
        ,ROUND(AVG(evolution_percent_AVG_duree_hospi),2) as evolution_percent_AVG_duree_hospi
        ,ROUND(AVG(tranche_age_0_1),2) as tranche_age_0_1
        ,ROUND(AVG(tranche_age_1_4),2) as tranche_age_1_4
        ,ROUND(AVG(tranche_age_5_14),2) as tranche_age_5_14
        ,ROUND(AVG(tranche_age_15_24),2) as tranche_age_15_24
        ,ROUND(AVG(tranche_age_25_34),2) as tranche_age_25_34
        ,ROUND(AVG(tranche_age_35_44),2) as tranche_age_35_44
        ,ROUND(AVG(tranche_age_45_54),2) as tranche_age_45_54
        ,ROUND(AVG(tranche_age_55_64),2) as tranche_age_55_64
        ,ROUND(AVG(tranche_age_65_74),2) as tranche_age_65_74
        ,ROUND(AVG(tranche_age_75_84),2) as tranche_age_75_84
        ,ROUND(AVG(tranche_age_85_et_plus),2) as tranche_age_85_et_plus
        ,ROUND(AVG(tx_brut_tt_age_pour_mille), 2) as tx_brut_tt_age_pour_mille
        ,ROUND(AVG(tx_standard_tt_age_pour_mille), 2) as tx_standard_tt_age_pour_mille
        ,ROUND(AVG(indice_comparatif_tt_age_percent), 2) as indice_comparatif_tt_age_percent
        ,ROUND(AVG(evolution_tx_brut_tt_age_pour_mille), 2) as evolution_tx_brut_tt_age_pour_mille
        ,ROUND(AVG(evolution_percent_tx_brut_tt_age_pour_mille), 2) as evolution_percent_tx_brut_tt_age_pour_mille
        ,ROUND(AVG(evolution_tx_standard_tt_age_pour_mille), 2) as evolution_tx_standard_tt_age_pour_mille
        ,ROUND(AVG(evolution_percent_tx_standard_tt_age_pour_mille), 2) as evolution_percent_tx_standard_tt_age_pour_mille
        ,ROUND(AVG(evolution_indice_comparatif_tt_age_percent), 2) as evolution_indice_comparatif_tt_age_percent
        ,ROUND(AVG(evolution_percent_indice_comparatif_tt_age_percent), 2) as evolution_percent_indice_comparatif_tt_age_percent
        ,ROUND(AVG(population),0) as population
    FROM {{ref("class_join_total_morbidite_population")}}
    GROUP BY
        niveau
        ,cle_unique
        ,sexe
        ,year
        ,annee
        ,region
        ,code_region
        ,nom_region
        ,classification
)

SELECT 
    t1.*
    ,t2.lit_hospi_complete
    ,t2.sejour_hospi_complete
    ,t2.journee_hospi_complete
    ,t2.place_hospi_partielle
    ,t2.sejour_hospi_partielle
    ,t2.passage_urgence
    ,t2.evolution_lit_hospi_complete1 as evolution_lit_hospi_complete
    ,t2.evolution_percent_lit_hospi_complete1 as evolution_percent_lit_hospi_complete
    ,t2.evolution_sejour_hospi_complete1 as evolution_sejour_hospi_complete
    ,t2.evolution_percent_sejour_hospi_complete1 as evolution_percent_sejour_hospi_complete
    ,t2.evolution_journee_hospi_complete1 as evolution_journee_hospi_complete
    ,t2.evolution_percent_journee_hospi_complete1 as evolution_percent_journee_hospi_complete
    ,t2.evolution_place_hospi_partielle1 as evolution_place_hospi_partielle
    ,t2.evolution_percent_place_hospi_partielle1 as evolution_percent_place_hospi_partielle
    ,t2.evolution_sejour_hospi_partielle1 as evolution_sejour_hospi_partielle
    ,t2.evolution_percent_sejour_hospi_partielle1 as evolution_percent_sejour_hospi_partielle
    ,t2.evolution_passage_urgence1 as evolution_passage_urgence
    ,t2.evolution_percent_passage_urgence1 as evolution_percent_passage_urgence
FROM agg_class t1
LEFT JOIN {{ref("mart_capacite_dpt_reg_evol")}} t2
ON t1.cle_unique = t2.cle_unique



