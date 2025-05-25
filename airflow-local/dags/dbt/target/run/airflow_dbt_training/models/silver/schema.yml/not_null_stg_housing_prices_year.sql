
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select year
from "dwh"."public_silver"."stg_housing_prices"
where year is null



  
  
      
    ) dbt_internal_test