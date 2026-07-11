{{
    config(
        materialized="incremental",
        unique_key="payroll_id",
        incremental_strategy="merge",
        on_schema_change = "append_new_columns"
    )
}}

with base as ( 
    select *
    from {{ref('payrolls')}} 
    where is_valid = 'VALID'
    {% if is_incremental() %}
        AND updated_at >
        (
            SELECT COALESCE(MAX(updated_at), '1900-01-01')
            FROM {{ this }}
        )
    {% endif %}
    
)
select 
p.* ,
e.department_id 
from base p 
left join {{ref('dim_employees')}} e 
on p.employee_id = e.employee_id 
