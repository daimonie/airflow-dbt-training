{% test valid_values(model, column_name, valid_values) %}
    SELECT *
    FROM {{ model }}
    WHERE {{ normalize_values(column_name, valid_values) }} = 'UNKNOWN'
{% endtest %} 