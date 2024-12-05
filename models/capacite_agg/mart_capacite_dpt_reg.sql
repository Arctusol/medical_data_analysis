WITH dpt as (
    SELECT
    annee,
    year,
    service_medical,
    service_classification,
    nom_etablissement,
    statut_juridique,
    categ_etablissement,
    departement as region,
    code_departement as code_region,
    nom_departement as nom_region,
    code_espic,
    lit_hospi_complete_detail,
    sejour_hospi_complete_detail,
    journee_hospi_complete_detail,
    place_hospi_partielle_detail,
    sejour_hospi_partielle_detail,
    passage_urgence_detail,
    sejour_accouchement_detail,
    seance_hemodyalise_detail,
    seance_radiotherapie_detail,
    seance_chimio_detail,
    total_lit_hospi_complete,
    total_sejour_hospi_complete,
    total_journee_hospi_complete,
    total_place_hospi_partielle,
    total_sejour_hospi_partielle,
    FROM {{ref("int_capacite_etablissement_join")}}
),
reg as (
    SELECT
    annee,
    year,
    service_medical,
    service_classification,
    nom_etablissement,
    statut_juridique,
    categ_etablissement,
    region,
    code_region,
    nom_region,
    code_espic,
    lit_hospi_complete_detail,
    sejour_hospi_complete_detail,
    journee_hospi_complete_detail,
    place_hospi_partielle_detail,
    sejour_hospi_partielle_detail,
    passage_urgence_detail,
    sejour_accouchement_detail,
    seance_hemodyalise_detail,
    seance_radiotherapie_detail,
    seance_chimio_detail,
    total_lit_hospi_complete,
    total_sejour_hospi_complete,
    total_journee_hospi_complete,
    total_place_hospi_partielle,
    total_sejour_hospi_partielle,
    FROM {{ref("int_capacite_etablissement_join")}}
),
union1 as (
SELECT *
FROM dpt
UNION ALL
SELECT *
FROM reg
)

SELECT
    annee,
    year,
    region,
    code_region,
    nom_region,
    service_medical,
    service_classification,
    SUM(lit_hospi_complete_detail) as lit_hospi_complete,
    SUM(sejour_hospi_complete_detail) as sejour_hospi_complete,
    SUM(journee_hospi_complete_detail) as journee_hospi_complete,
    SUM(place_hospi_partielle_detail) as place_hospi_partielle,
    SUM(sejour_hospi_partielle_detail) as sejour_hospi_partielle,
    SUM(passage_urgence_detail) as passage_urgence,
    SUM(sejour_accouchement_detail) as sejour_accouchement,
    SUM(seance_hemodyalise_detail) as seance_hemodyalise,
    SUM(seance_radiotherapie_detail) as seance_radiotherapie,
    SUM(seance_chimio_detail) as seance_chimio,
FROM union1
GROUP BY
    annee,
    year,
    region,
    code_region,
    nom_region,
    service_medical,
    service_classification






