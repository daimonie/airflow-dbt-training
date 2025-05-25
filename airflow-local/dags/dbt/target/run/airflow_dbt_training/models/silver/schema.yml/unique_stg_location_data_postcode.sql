
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    postcode as unique_field,
    count(*) as n_records

from "dwh"."public_silver"."stg_location_data"
where postcode is not null
group by postcode
having count(*) > 1



  
  
      
    ) dbt_internal_test