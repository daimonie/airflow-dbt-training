{{ config(materialized='ephemeral') }}  -- or use 'view' if you want to inspect it

WITH source AS (
    SELECT * FROM {{ ref('housing_prices') }}
)

SELECT
    id,
    date::DATE as date,
    region,
    price,
    EXTRACT(YEAR FROM date::DATE) as year,
    EXTRACT(MONTH FROM date::DATE) as month,
    EXTRACT(DOW FROM date::DATE) as day_of_week,
    CURRENT_TIMESTAMP as updated_at
FROM source
