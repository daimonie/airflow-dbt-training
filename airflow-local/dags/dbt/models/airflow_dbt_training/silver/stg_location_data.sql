WITH source AS (
    SELECT * FROM {{ source('public', 'raw_location_data') }}
)

SELECT
    postcode,
    UPPER(region) as region,
    -- INITCAP capitalizes the first letter of each word and makes the rest lowercase
    -- e.g. 'URBAN' -> 'Urban', 'rural' -> 'Rural'
    INITCAP(type) as type,
    {{ normalize_values('"type"', ['URBAN', 'RURAL', 'RANDSTAD'], 'UNKNOWN') }} as type_normalized,
    {{ normalize_values_simpler('type', 'urban', 'rural', 'unknown') }} as type_norm_simpler
FROM source 