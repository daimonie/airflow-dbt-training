WITH avg_prices AS (
  SELECT
    region,
    AVG(price) AS avg_price,
    COUNT(*) AS n_sales
  FROM {{ ref('stg_housing_prices') }}
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
LEFT JOIN {{ ref('region_type_composition') }} r
  ON p.region = r.region
