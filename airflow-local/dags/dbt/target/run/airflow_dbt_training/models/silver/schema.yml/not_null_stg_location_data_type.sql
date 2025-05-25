
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select type
from "dwh"."public_silver"."stg_location_data"
where type is null



  
  
      
    ) dbt_internal_test