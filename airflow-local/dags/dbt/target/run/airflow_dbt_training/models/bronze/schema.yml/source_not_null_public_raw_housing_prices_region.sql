
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select region
from "dwh"."public"."raw_housing_prices"
where region is null



  
  
      
    ) dbt_internal_test