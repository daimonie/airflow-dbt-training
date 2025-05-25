
  create view "dwh"."public_bronze"."housing_prices__dbt_tmp"
    
    
  as (
    SELECT * 
FROM "dwh"."public"."raw_housing_prices"
  );