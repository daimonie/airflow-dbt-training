{% macro join_grain_test(table_one, table_two, column) %}
	WITH table_one AS (
		SELECT {{ column }}, COUNT(*) AS count_one FROM {{ table_one }}
	)
	, table_two AS (
		SELECT {{ column }}, COUNT(*) AS count_two FROM {{ table_two }}
	) ,
	joined (
		SELECT * FROM {{ table_one }} LEFT JOIN {{ table_two }} USING ({{ column }})
		UNION ALL
		SELECT * FROM {{ table_two }} LEFT JOIN {{ table_one }} USING ({{ column }})
	)
	SELECT * FROM joined
	WHERE count_one != count_two
{% endmacro %}