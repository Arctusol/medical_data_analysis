WITH 
join_dpt AS (
    SELECT
        t1.*,
        t2.population AS population
    FROM {{ ref("class_join_total_morbidite") }} t1
    LEFT JOIN {{ ref("stg_pop_departement__population_departement") }} t2
        ON t1.annee = t2.annee
        AND t1.nom_region = t2.nom_departement
    WHERE t1.niveau = 'Départements'  
),    
join_reg AS (
    SELECT
        t1.*,
        t2.population AS population
    FROM {{ ref("class_join_total_morbidite") }} t1
    LEFT JOIN {{ ref("stg_pop_departement__population_region") }} t2
        ON t1.annee = t2.annee
        AND t1.nom_region = t2.region
    WHERE t1.niveau = 'Régions'
)

SELECT *
FROM join_dpt
UNION ALL
SELECT *
FROM join_reg