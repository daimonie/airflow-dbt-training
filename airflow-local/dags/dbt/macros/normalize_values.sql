{%- macro normalize_values(column_name, accepted_values, default_value='UNKNOWN') -%}
-- this macro will normalize the values to accepted_values
-- input: column_name: the column to normalize
-- input: the accepted values in a list, e.g. ["Fruit", "Vegetable"] 
-- default_value: The default if nothing matches in accepted_value   

    CASE
        {%- for value in accepted_values %}
        WHEN LOWER({{ column_name }}) = LOWER('{{ value }}') THEN '{{ value }}'
        {%- endfor %}
        ELSE '{{ default_value }}'
    END
{%- endmacro -%}