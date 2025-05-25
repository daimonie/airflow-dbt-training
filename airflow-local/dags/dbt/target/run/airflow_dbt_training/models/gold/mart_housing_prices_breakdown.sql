
  create view "dwh"."public_gold"."mart_housing_prices_breakdown__dbt_tmp"
    
    
  as (
    WITH avg_prices AS (
  SELECT
    region,
    AVG(price) AS avg_price,
    COUNT(*) AS n_sales
  FROM "dwh"."public_silver"."stg_housing_prices"
  GROUP BY region
)

SELECT
  p.region,
  p.avg_price,
  p.n_sales,
  r.urban_count,
  r.rural_count,
  r.pct_urban
FROM avg_prices p
LEFT JOIN "dwh"."public_gold"."region_type_composition" r
  ON p.region = r.region
  );