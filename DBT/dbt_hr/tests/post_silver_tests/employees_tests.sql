SELECT * 
FROM {{ref('employees')}}
WHERE is_valid = 'VALID'
AND ( 
    employee_id is null 
    OR job_id is null 
    OR department_id is null 
    OR hire_date > CURRENT_DATE() 
) 
