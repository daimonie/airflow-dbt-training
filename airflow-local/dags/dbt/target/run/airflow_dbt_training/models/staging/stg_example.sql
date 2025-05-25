
  create view "dwh"."public"."stg_example__dbt_tmp"
    
    
  as (
    with source_data as (
    select 1 as id, 'test' as name
    union all
    select 2 as id, 'example' as name
)

select *
from source_data
  );