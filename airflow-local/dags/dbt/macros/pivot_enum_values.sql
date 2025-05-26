{% macro pivot_enum_values(column_name, values, include_total=true) %}
  {% for val in values %}
    COUNT(*) FILTER (WHERE {{ normalize_values(column_name, [val]) }} = '{{ val }}') AS {{ val | lower }}_count
    {%- if not loop.last %},{% endif %}
  {% endfor %}
  {%- if include_total %}
    {%- if values|length > 0 %},{% endif %}
    COUNT(*) AS total_count
  {%- endif %}
{% endmacro %}