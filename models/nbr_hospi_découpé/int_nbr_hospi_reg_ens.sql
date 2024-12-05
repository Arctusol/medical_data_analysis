SELECT 
    niveau,
    CONCAT(region,"_",code_pathologie,"_",sexe) as cle_unique,
    sexe,
    year,
    pathologie,
    code_pathologie,
    nom_pathologie,
    region,
    code_region,
    nom_region,
    code_age,
    tranche_age,
    nbr_hospi,
FROM {{ref("stg_morbidite_h__nombre_hospit2")}}
WHERE NOT (region LIKE '3 - France%' OR region LIKE '1 - France%')
    AND niveau LIKE "Régions"
    AND nom_pathologie != 'TOTAL TOUTES CAUSES'
    AND (pathologie NOT LIKE '%000%'OR pathologie LIKE "%Covid%")
    AND sexe LIKE "Ensemble"
ORDER BY cle_unique