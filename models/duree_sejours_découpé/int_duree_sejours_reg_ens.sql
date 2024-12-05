SELECT niveau,
    CONCAT(region,"_",code_pathologie,"_",annee) as cle_unique,
    annee,
    year,
    pathologie,
    code_pathologie,
    nom_pathologie,
    region,
    code_region,
    nom_region,
    hospi_prog_24h,
    hospi_autres_24h,
    hospi_total_24h,
    hospi_1J,
    hospi_2J,
    hospi_3J,
    hospi_4J,
    hospi_5J,
    hospi_6J,
    hospi_7J,
    hospi_8J,
    hospi_9J,
    hospi_10J_19J,
    hospi_20J_29J,
    hospi_30J,
    (total_hospi - hospi_total_24h) AS hospi_total_jj,
    total_hospi,
    AVG_duree_hospi

FROM {{ref("stg_morbidite_h__duree_sejours2")}}
WHERE NOT (region LIKE '3 - France%' OR region LIKE '1 - France%')
    AND niveau LIKE "Régions"
    AND nom_pathologie != 'TOTAL TOUTES CAUSES'
    AND (pathologie NOT LIKE '%000%'OR pathologie LIKE "%Covid%")
ORDER BY cle_unique
