
select 
job_id ,
dbt_scd_id as job_key ,
department_id ,
job_title ,
job_level ,
min_salary ,
max_salary ,
created_at ,
updated_at ,
ingest_at ,
dbt_valid_from ,
dbt_valid_to ,
True as is_current 
from {{ref('job_history')}}
where dbt_valid_to is null 
