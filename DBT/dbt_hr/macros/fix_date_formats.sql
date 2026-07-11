{% macro fix_date_formats(col) %}

COALESCE(
    TRY_TO_DATE({{ col }}, 'YYYY-MM-DD'),
    TRY_TO_DATE({{ col }}, 'DD-MM-YYYY'),
    TRY_TO_DATE({{ col }}, 'YYYY/MM/DD'),
    TRY_TO_DATE({{ col }}, 'DD/MM/YYYY'),
    TRY_TO_DATE({{ col }}, 'MM-DD-YYYY'),
    TRY_TO_DATE({{ col }}, 'MM/DD/YYYY'),
    TRY_TO_DATE({{ col }}, 'YYYY.MM.DD'),
    TRY_TO_DATE({{ col }}, 'DD.MM.YYYY'),
    TRY_TO_DATE({{ col }}, 'YYYYMMDD'),
    TRY_TO_DATE({{ col }}, 'DDMMYYYY')
)

{% endmacro %}