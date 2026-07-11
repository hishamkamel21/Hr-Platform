with base as ( 
    select 
        employee_id,
        type,
        reason,
        last_working_day,
        created_at,
        updated_at,
        ingest_at,

        case 
            when employee_id is null 
              or type is null 
              or reason is null 
              or last_working_day is null 
               then 'NULL_ERROR'
            when last_working_day > current_date() 
               then 'FUTURE_DATE_ERROR'
        end as error_type,

        case 
            when employee_id is null then 'employee_id'
            when type is null then 'type'
            when reason is null then 'reason'
            when last_working_day is null or last_working_day > current_date() then 'last_working_day'
        end as error_column

    from {{ ref('seprations') }} 
    where is_valid = 'INVALID'
)
select * from base