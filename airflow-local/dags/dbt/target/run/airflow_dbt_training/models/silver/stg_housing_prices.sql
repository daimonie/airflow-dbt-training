
  create view "dwh"."public_silver"."stg_housing_prices__dbt_tmp"
    
    
  as (
    WITH source AS (
    SELECT * FROM "dwh"."public_bronze"."housing_prices"
)

SELECT
    id,
    date::DATE as date,
    region,
    price,
    EXTRACT(YEAR FROM date::DATE) as year,
    EXTRACT(MONTH FROM date::DATE) as month,
    EXTRACT(DOW FROM date::DATE) as day_of_week
FROM source
  );