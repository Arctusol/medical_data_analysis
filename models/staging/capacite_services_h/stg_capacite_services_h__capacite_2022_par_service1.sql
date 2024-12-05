with 

source as (

    select * from {{ source('capacite_services_h', 'capacite_2022_par_service1') }}

),

renamed as (

    select
        annee,
        nom_etablissement,
        statut_juridique,
        categ_etablissement,
        departement,
        code_departement,
        nom_departement,
        region,
        code_region,
        nom_region,
        code_espic,
        discipline_equipement,
        service_medical,
        lit_hospi_complete,
        sejour_hospi_complete,
        journee_hospi_complete,
        place_hospi_partielle,
        sejour_hospi_partielle,
        passage_urgence,
        sejour_accouchement,
        seance_hemodyalise,
        seance_radiotherapie,
        seance_chimio

    from source

)

select * from renamed
