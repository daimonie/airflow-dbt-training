
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select day_of_week
from "dwh"."public_silver"."stg_housing_prices"
where day_of_week is null



  
  
      
    ) dbt_internal_test