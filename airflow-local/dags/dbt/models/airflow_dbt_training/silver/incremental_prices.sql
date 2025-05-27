{{ config(materialized='incremental', incremental_strategy='append', unique_key='id') }}
SELECT

    id,
    date,
    region,
    price,
    year,
    month,
    day_of_week,
    updated_at

FROM {{ ref('stg_housing_prices') }}
{% if is_incremental() %}
WHERE updated_at > (SELECT updated_at FROM {{ this }} ORDER BY updated_at DESC LIMIT 1)
{% endif %}