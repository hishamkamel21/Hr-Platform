{% macro accepted_values(col, accepted_values, alias) %}

CASE
    WHEN {{ col }} IS NULL THEN NULL 

    WHEN UPPER(TRIM({{ col }})) = '' THEN NULL 

    WHEN UPPER(TRIM({{ col }})) NOT IN {{ accepted_values }}
        THEN NULL 

    ELSE UPPER(TRIM({{ col }}))

END AS {{ alias }}

{% endmacro %} 

