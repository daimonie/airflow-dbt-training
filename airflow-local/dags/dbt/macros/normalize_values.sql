{%- macro normalize_values(column_name, accepted_values, default_value='UNKNOWN') -%}
    CASE
        {%- for value in accepted_values %}
        WHEN LOWER({{ column_name }}) = LOWER('{{ value }}') THEN '{{ value }}'
        {%- endfor %}
        ELSE '{{ default_value }}'
    END
{%- endmacro -%} 