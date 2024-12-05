with 

source as (

    select * from {{ source('morbidite_h', 'nombre_hospit2') }}

),

renamed as (

    select
        niveau,
        annee,
        DATE(CAST(annee AS STRING) || "-12-31") as year,
        pathologie,
        SPLIT(pathologie, "-")[SAFE_OFFSET(0)] AS code_pathologie,
        SPLIT(pathologie, "-")[SAFE_OFFSET(1)] AS nom_pathologie,
        region,
        SPLIT(region, " - ")[SAFE_OFFSET(0)] AS code_region,
        SPLIT(region, " - ")[SAFE_OFFSET(1)] AS nom_region,
        sexe,
        age,
        CAST(SPLIT(age, "-")[SAFE_OFFSET(0)] AS INT64) AS code_age,
        SPLIT(age, "-")[SAFE_OFFSET(1)] AS tranche_age,
        nbr_hospi

    from source

)

select * from renamed
