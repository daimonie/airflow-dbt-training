
  create view "dwh"."public_bronze"."location_data__dbt_tmp"
    
    
  as (
    SELECT * FROM public.raw_location_data
  );