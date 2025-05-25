WITH source AS (
    SELECT * FROM "dwh"."public"."raw_location_data"
)

SELECT
    postcode,
    UPPER(region) as region,
    -- INITCAP capitalizes the first letter of each word and makes the rest lowercase
    -- e.g. 'URBAN' -> 'Urban', 'rural' -> 'Rural'
    INITCAP(type) as type
FROM source