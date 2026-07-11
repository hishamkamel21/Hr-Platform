
select 
employee_id ,
dbt_scd_id as employee_key , 
full_name ,
email ,
phone ,
gender ,
age , 
date_of_birth,
hire_date ,
termination_date ,
manager_id ,
department_id ,
job_id ,
employee_status ,
education_level ,
month_salary ,
created_at ,
updated_at ,
ingest_at ,
dbt_valid_from ,
dbt_valid_to ,
True as is_current 
from {{ref('employee_history')}} 
where dbt_valid_to is null 