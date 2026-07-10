
select 
department_id ,
dbt_scd_id as department_key , 
department_name ,
manager_id ,
total_employees ,
total_active_employees ,
total_terminated_employees ,
avg_employees_age ,
created_at ,
updated_at ,
ingest_at ,
dbt_valid_from ,
dbt_valid_to ,
TRUE as is_current
from {{ref('department_history')}} 
where dbt_valid_to is null 
