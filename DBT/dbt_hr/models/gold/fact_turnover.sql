{{
    config(
        materialized="incremental",
        unique_key="employee_id",
        incremental_strategy="merge",
        on_schema_change = "append_new_columns"
    )
}}

with base as ( 
    select * 
    from {{ref('seprations')}} 
    {% if is_incremental() %}
        AND updated_at >
        (
            SELECT COALESCE(MAX(updated_at), '1900-01-01')
            FROM {{ this }}
        )
    {% endif %}
),
turnover as ( 
    select 
    t.* ,
    e.hire_date , 
    DATEDIFF(day,e.hire_date,t.last_working_day) as work_for_days 

    from base t 
    left join {{ref('employees')}} e 
    on t.employee_id = e.employee_id 
)
select * 
from turnover  

