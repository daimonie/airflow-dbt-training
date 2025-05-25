
    
    

select
    id as unique_field,
    count(*) as n_records

from "dwh"."public"."raw_housing_prices"
where id is not null
group by id
having count(*) > 1


