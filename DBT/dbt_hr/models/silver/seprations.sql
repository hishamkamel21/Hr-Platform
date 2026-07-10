{{
    config(
        materialized="incremental",
        unique_key="employee_id",
        incremental_strategy="merge",
        on_schema_change = "append_new_columns"
    )
}}
with base as ( 
    select 
    {{handle_Ids('employee_id')}} as employee_id,
    UPPER(TRIM(type)) as type ,
    coalesce(reason,'N/A') as reason ,
    {{fix_date_formats('last_working_day')}} as last_working_day,
    created_at ,
    updated_at ,
    ingest_at 

    from {{source('bronze','seprations')}} 
    {% if is_incremental() %}
        where updated_at >
        (
            SELECT COALESCE(MAX(updated_at), '1900-01-01')
            FROM {{ this }}
        )
    {% endif %}
),
stage as ( 
    select *
    from base 
    qualify row_number() over(
        partition by employee_id 
        order by updated_at 
    ) = 1 
)
select * ,
case 
  when employee_id is null 
   or type is null 
   or reason is null 
   or last_working_day is null 
   or last_working_day > CURRENT_DATE()
  then 'INVALID'
  else 'VALID'
end as is_valid
   
from stage 