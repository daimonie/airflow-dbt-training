WITH type_counts AS (
  SELECT
    region,
    {{ pivot_enum_values('type', ['URBAN', 'RURAL'], include_total=true) }}
  FROM {{ ref('stg_location_data') }}
  GROUP BY region
)

SELECT
  region,
  urban_count,
  rural_count,
  total_count AS total_locations,
  ROUND(urban_count * 1.0 / total_count, 2) AS pct_urban
FROM type_counts
