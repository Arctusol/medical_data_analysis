SELECT 
fi as id_etablissement,
an as annee,
rs as nom_etablissement,
stj as statut_juridique,
cat as categ_etablissement,
dep as departement,
SPLIT(dep, " - ")[SAFE_OFFSET(0)] AS code_departement,
SPLIT(dep, " - ")[SAFE_OFFSET(1)] AS nom_departement,
reg as region,
SPLIT(reg, " - ")[SAFE_OFFSET(0)] AS code_region,
SPLIT(reg, " - ")[SAFE_OFFSET(1)] AS nom_region,
espic as code_espic,
LIT as lit_hospi_complete,
SEJHC as sejour_hospi_complete,
JOU as journee_hospi_complete,
PLA as place_hospi_partielle,
SEJHP as sejour_hospi_partielle,
PAS as passage_urgence,
SEJACC as sejour_accouchement,
SEHEM as seance_hemodyalise,
SERAD as seance_radiotherapie,
SECHI as seance_chimio,
 FROM {{ref("stg_capacite_services_h__capacite_2022_par_etablissement")}}
WHERE an >= 2018