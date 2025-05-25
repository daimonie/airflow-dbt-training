
    
    

select
    postcode as unique_field,
    count(*) as n_records

from "dwh"."public_silver"."stg_location_data"
where postcode is not null
group by postcode
having count(*) > 1


