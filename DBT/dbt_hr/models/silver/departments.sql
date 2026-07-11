{{
    config(
        materialized="incremental",
        unique_key="department_id",
        incremental_strategy="merge",
        on_schema_change = "append_new_columns"
    )
}}

with base as ( 
    select 
    {{ handle_Ids('department_id') }} as department_id,
    UPPER(TRIM(department_name)) as department_name,
    {{ handle_Ids('manager_id')}} as manager_id ,
    created_at ,
    updated_at ,
    ingest_at 

    from {{source('bronze','departments')}} 
    {% if is_incremental() %}
        WHERE updated_at >
        (
            SELECT COALESCE(MAX(updated_at), '1900-01-01')
            FROM {{ this }}
        )
    {% endif %}

),
stage as (
    select 
    * 
    from base 
    qualify row_number() over (
        partition by department_id 
        order by updated_at desc 
    ) = 1 
),
enriched as ( 
    select 
    d.* ,
    t.Total_Employees ,
    t.Total_Active_Employees ,
    t.Total_Terminated_Employees ,
    t.Avg_Employees_Age
    
    from stage d 
    left join {{ref('total_employees')}} t 
    on d.department_id = t.department_id
)
select 
* ,
case 
  when department_id is null or 
   department_name is null or
   manager_id is null 
  then 'INVALID'
  else 'VALID'
end as is_valid 

from enriched 


