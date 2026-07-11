SELECT * 
FROM {{ref('jobs')}}
where
    job_id is null 
    OR department_id is null 
    OR min_salary is null 
    OR max_salary is null 
    OR min_salary < 0 
    OR max_salary < 0 
    OR min_salary > max_salary 

