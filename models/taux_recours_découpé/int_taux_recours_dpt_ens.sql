SELECT 
niveau,
CONCAT(region,"_",code_pathologie,"_",sexe) as cle_unique,
sexe,
pathologie,
SAFE_CAST(NULLIF(code_pathologie, 'ND') AS INT64) AS code_pathologie,
nom_pathologie,
DATE(CAST(annee AS STRING) || "-12-31") as year,
region as departement,
SPLIT(region, " - ")[SAFE_OFFSET(0)] AS code_departement,
SPLIT(region, " - ")[SAFE_OFFSET(1)] AS nom_departement,
  SAFE_CAST(NULLIF(tranche_age_0_1, 'ND') AS FLOAT64) AS tranche_age_0_1,  
  SAFE_CAST(NULLIF(tranche_age_1_4, 'ND') AS FLOAT64) AS tranche_age_1_4,
  SAFE_CAST(NULLIF(tranche_age_5_14, 'ND') AS FLOAT64) AS tranche_age_5_14,
  SAFE_CAST(NULLIF(tranche_age_15_24, 'ND') AS FLOAT64) AS tranche_age_15_24,
  SAFE_CAST(NULLIF(tranche_age_25_34, 'ND') AS FLOAT64) AS tranche_age_25_34,
  SAFE_CAST(NULLIF(tranche_age_35_44, 'ND') AS FLOAT64) AS tranche_age_35_44,
  SAFE_CAST(NULLIF(tranche_age_45_54, 'ND') AS FLOAT64) AS tranche_age_45_54,
  SAFE_CAST(NULLIF(tranche_age_55_64, 'ND') AS FLOAT64) AS tranche_age_55_64,
  SAFE_CAST(NULLIF(tranche_age_65_74, 'ND') AS FLOAT64) AS tranche_age_65_74,
  SAFE_CAST(NULLIF(tranche_age_75_84, 'ND') AS FLOAT64) AS tranche_age_75_84,
  SAFE_CAST(NULLIF(tranche_age_85_et_plus, 'ND') AS FLOAT64) AS tranche_age_85_et_plus,
  SAFE_CAST(NULLIF(tx_brut_tt_age_pour_mille, 'ND') AS FLOAT64) AS tx_brut_tt_age_pour_mille,
  SAFE_CAST(NULLIF(tx_standard_tt_age_pour_mille, 'ND') AS FLOAT64) AS tx_standard_tt_age_pour_mille,
  SAFE_CAST(NULLIF(indice_comparatif_tt_age_percent, 'ND') AS FLOAT64) AS indice_comparatif_tt_age_percent
 FROM {{ref("stg_morbidite_h__taux_recours2")}}
 WHERE NOT (region LIKE '3 - France%' OR region LIKE '1 - France%')
  AND niveau LIKE "Départements"
  AND nom_pathologie != 'TOTAL TOUTES CAUSES'
  AND (pathologie NOT LIKE '%000%'OR pathologie LIKE "%Covid%")
  AND sexe LIKE "Ensemble"
ORDER BY cle_unique