
  create view "dwh"."public_gold"."region_type_composition__dbt_tmp"
    
    
  as (
    WITH type_counts AS (
  SELECT
    region,
    COUNT(*) FILTER (WHERE type = 'URBAN') AS urban_count,
    COUNT(*) FILTER (WHERE type = 'RURAL') AS rural_count,
    COUNT(*) AS total_locations
  FROM "dwh"."public_silver"."stg_location_data"
  GROUP BY region
)

SELECT
  region,
  urban_count,
  rural_count,
  ROUND(urban_count * 1.0 / total_locations, 2) AS pct_urban
FROM type_counts
  );