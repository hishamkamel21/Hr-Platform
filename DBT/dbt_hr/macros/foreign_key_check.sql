{% macro foreign_key_check(
    main,
    ref_model,
    foreign_key,
    alias,
    add_ref_validity=false,
    ref_foreign_key=None
) %}

CASE
    WHEN NOT EXISTS (

        SELECT 1
        FROM {{ ref(ref_model) }} AS ref_table

        WHERE

        {% if ref_foreign_key %}
            {{ main }}.{{ foreign_key }} = ref_table.{{ ref_foreign_key }}
        {% else %}
            {{ main }}.{{ foreign_key }} = ref_table.{{ foreign_key }}
        {% endif %}
        {% if add_ref_validity %}
            AND ref_table.is_valid = 'VALID'
        {% endif %}

    )
    THEN 1
    ELSE 0

END AS {{ alias }}

{% endmacro %}