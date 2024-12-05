with 

source as (

    select * from {{ source('morbidite_h', 'taux_recours2') }}

),

renamed as (

    select
        niveau,
        sexe,
        annee,
        DATE(CAST(annee AS STRING) || "-12-31") as year,
        pathologie,
        SPLIT(pathologie, "-")[SAFE_OFFSET(0)] AS code_pathologie,
        SPLIT(pathologie, "-")[SAFE_OFFSET(1)] AS nom_pathologie,
        region,
        SPLIT(region, " - ")[SAFE_OFFSET(0)] AS code_region,
        SPLIT(region, " - ")[SAFE_OFFSET(1)] AS nom_region,
        tranche_age_0_1,
        tranche_age_1_4,
        tranche_age_5_14,
        tranche_age_15_24,
        tranche_age_25_34,
        tranche_age_35_44,
        tranche_age_45_54,
        tranche_age_55_64,
        tranche_age_65_74,
        tranche_age_75_84,
        tranche_age_85_et_plus,
        tx_brut_tt_age_pour_mille,
        tx_standard_tt_age_pour_mille,
        indice_comparatif_tt_age_percent

    from source

)

select * from renamed
