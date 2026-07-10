with base as ( 
    select 
        employee_id,
        full_name,
        email,
        phone,
        gender,
        age,
        date_of_birth, 
        hire_date,
        termination_date,
        manager_id,
        department_id,
        job_id,
        employee_status,
        education_level,
        created_at,
        updated_at,
        ingest_at,

        case 
            when employee_id is null 
              or job_id is null 
              or department_id is null 
               then 'NULL_ERROR'
            when hire_date > current_date() 
              or termination_date > current_date() 
               then 'FUTURE_DATE_ERROR'
        end as error_type,

        case 
            when employee_id is null then 'employee_id'
            when job_id is null then 'job_id'
            when department_id is null then 'department_id'
            when hire_date > current_date() then 'hire_date'
            when termination_date > current_date() then 'termination_date'
        end as error_column

    from {{ ref('employees') }} 
    where is_valid = 'INVALID'
)
select * from base