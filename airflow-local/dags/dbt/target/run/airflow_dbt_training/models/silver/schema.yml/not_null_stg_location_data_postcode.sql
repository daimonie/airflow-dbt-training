
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select postcode
from "dwh"."public_silver"."stg_location_data"
where postcode is null



  
  
      
    ) dbt_internal_test