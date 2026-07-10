with base as ( 
    select 
        department_id,
        department_name,
        manager_id,
        created_at,
        updated_at,
        ingest_at,
        total_employees,
        total_active_employees,
        total_terminated_employees,
        avg_employees_age,

        case 
            when department_id is null 
              or department_name is null 
              or manager_id is null 
               then 'NULL_ERROR'
        end as error_type,

        case 
            when department_id is null then 'department_id'
            when department_name is null then 'department_name'
            when manager_id is null then 'manager_id'
        end as error_column

    from {{ ref('departments') }} 
    where is_valid = 'INVALID'
)
select * from base