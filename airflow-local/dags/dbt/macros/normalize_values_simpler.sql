{%- macro normalize_values_simpler(column_name, value1, value2, default_value='UNKNOWN') -%}
    CASE 
        WHEN LOWER({{ column_name }}) = LOWER('{{ value1 }}') THEN '{{ value1 }}'
 
        WHEN LOWER({{ column_name }}) = LOWER('{{ value2 }}') THEN '{{ value2 }}'
 
        ELSE '{{ default_value }}'
    END
{%- endmacro -%}  