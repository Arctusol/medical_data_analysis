SELECT
    niveau,
    CONCAT(region,"_",code_pathologie,"_",annee) as cle_unique,
    sexe,
    year,
    EXTRACT(year from year) as annee,
    pathologie,
    code_pathologie,
    nom_pathologie,
    region,
    code_region,
    nom_region,
    age,
    code_age,
    tranche_age,
    nbr_hospi,
FROM {{ref("stg_morbidite_h__nombre_hospit2")}}
WHERE NOT (region LIKE '3 - France%' OR region LIKE '1 - France%')
    AND niveau NOT LIKE "France"
    AND nom_pathologie != 'TOTAL TOUTES CAUSES'
    AND (pathologie NOT LIKE '%000%'OR pathologie LIKE "%Covid%")
