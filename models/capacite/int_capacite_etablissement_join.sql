With join_capacite as (
    SELECT 
  t2.annee as annee,
  DATE(CAST(t2.annee AS STRING) || "-12-31") as year,
  t2.service_medical,
  t1.nom_etablissement AS nom_etablissement,
  t1.statut_juridique AS statut_juridique,
  t1.categ_etablissement AS categ_etablissement,
  t1.departement AS departement,
  t1.code_departement AS code_departement,
  t1.nom_departement AS nom_departement,
  t1.region AS region,
  t1.code_region AS code_region,
  t1.nom_region AS nom_region,
  t1.code_espic AS code_espic,
  t2.lit_hospi_complete AS lit_hospi_complete_detail,
  t2.sejour_hospi_complete AS sejour_hospi_complete_detail,
  t2.journee_hospi_complete AS journee_hospi_complete_detail,
  t2.place_hospi_partielle AS place_hospi_partielle_detail,
  t2.sejour_hospi_partielle AS sejour_hospi_partielle_detail,
  t2.passage_urgence AS passage_urgence_detail,
  t2.sejour_accouchement AS sejour_accouchement_detail,
  t2.seance_hemodyalise AS seance_hemodyalise_detail,
  t2.seance_radiotherapie AS seance_radiotherapie_detail,
  t2.seance_chimio AS seance_chimio_detail,
  t1.lit_hospi_complete AS total_lit_hospi_complete,
  t1.sejour_hospi_complete AS total_sejour_hospi_complete,
  t1.journee_hospi_complete AS total_journee_hospi_complete,
  t1.place_hospi_partielle AS total_place_hospi_partielle,
  t1.sejour_hospi_partielle AS total_sejour_hospi_partielle,
FROM 
  {{ref("stg_capacite_services_h__capacite_2022_par_etablissement1")}} AS t1
JOIN 
  {{ref("stg_capacite_services_h__capacite_2022_par_service1")}} AS t2
ON 
  t1.nom_etablissement = t2.nom_etablissement
  AND t1.annee = t2.annee
)

SELECT *, 
  CASE 
        WHEN service_medical = 'Soins de suite et réadaptation' THEN 'SSR'
        WHEN service_medical = 'Gynéco-Obstétrique' THEN 'O'
        WHEN service_medical = 'Médecine' THEN 'M'
        WHEN service_medical = 'Chirurgie' THEN 'C'
        WHEN service_medical = 'Soins de longue durée' THEN 'ESND'
        WHEN service_medical = 'Psychiatrie' THEN 'PSY'
        WHEN service_medical = 'Hospitalisation à domicile' THEN NULL
END AS service_classification ,
FROM `join_capacite` 
