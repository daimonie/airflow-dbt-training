
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select price
from "dwh"."public_silver"."stg_housing_prices"
where price is null



  
  
      
    ) dbt_internal_test