with 

source as (

    select * from {{ source('morbidite_h', 'duree_sejours2') }}

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
        SAFE_CAST(NULLIF(hospi_prog_24h, 'ND') AS FLOAT64) AS hospi_prog_24h,
        SAFE_CAST(NULLIF(hospi_autres_24h, 'ND') AS FLOAT64) AS hospi_autres_24h,
        SAFE_CAST(NULLIF(hospi_total_24h, 'ND') AS FLOAT64) AS hospi_total_24h,
        SAFE_CAST(NULLIF(hospi_1j, 'ND') AS FLOAT64) AS hospi_1j,
        SAFE_CAST(NULLIF(hospi_2j, 'ND') AS FLOAT64) AS hospi_2j,
        SAFE_CAST(NULLIF(hospi_3j, 'ND') AS FLOAT64) AS hospi_3j,
        SAFE_CAST(NULLIF(hospi_4j, 'ND') AS FLOAT64) AS hospi_4j,
        SAFE_CAST(NULLIF(hospi_5j, 'ND') AS FLOAT64) AS hospi_5j,
        SAFE_CAST(NULLIF(hospi_6j, 'ND') AS FLOAT64) AS hospi_6j,
        SAFE_CAST(NULLIF(hospi_7j, 'ND') AS FLOAT64) AS hospi_7j,
        SAFE_CAST(NULLIF(hospi_8j, 'ND') AS FLOAT64) AS hospi_8j,
        SAFE_CAST(NULLIF(hospi_9j, 'ND') AS FLOAT64) AS hospi_9j,
        SAFE_CAST(NULLIF(hospi_10j_19j, 'ND') AS FLOAT64) AS hospi_10j_19j,
        SAFE_CAST(NULLIF(hospi_20j_29j, 'ND') AS FLOAT64) AS hospi_20j_29j,
        SAFE_CAST(NULLIF(hospi_30j, 'ND') AS FLOAT64) AS hospi_30j,
        SAFE_CAST(NULLIF(total_hospi, 'ND') AS FLOAT64) AS total_hospi,
        SAFE_CAST(NULLIF(avg_duree_hospi, 'ND') AS FLOAT64) AS avg_duree_hospi

    from source

)

select * from renamed
