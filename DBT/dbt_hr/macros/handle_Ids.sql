{% macro handle_Ids(col) %}

CASE
    WHEN {{ col }} IS NULL THEN NULL
    WHEN UPPER(TRIM({{ col }})) = '' THEN NULL
    ELSE UPPER(TRIM({{ col }}))
END

{% endmacro %} 