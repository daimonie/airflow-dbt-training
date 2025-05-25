
    
    

with all_values as (

    select
        day_of_week as value_field,
        count(*) as n_records

    from "dwh"."public_silver"."stg_housing_prices"
    group by day_of_week

)

select *
from all_values
where value_field not in (
    '0','1','2','3','4','5','6'
)


