with base as ( 
    select 
        post_id,
        job_id,
        posted_by,
        platform,
        posted_at,
        expires_at,
        created_at,
        updated_at,
        ingest_at,
        foreign_job_error,
        foreign_employee_error,

        case 
            when post_id is null 
              or job_id is null 
              or posted_by is null 
              or platform is null 
              or posted_at is null 
               then 'NULL_ERROR'
            when foreign_job_error = 1 
              or foreign_employee_error = 1 
               then 'FOREIGN_KEY_ERROR'
            when posted_at > current_timestamp() 
               then 'FUTURE_DATE_ERROR'
            when posted_at > expires_at 
               then 'LOGICAL_DATE_ERROR'
        end as error_type,

        case 
            when post_id is null then 'post_id'
            when job_id is null or foreign_job_error = 1 then 'job_id'
            when posted_by is null or foreign_employee_error = 1 then 'posted_by'
            when platform is null then 'platform'
            when posted_at is null or posted_at > current_timestamp() or posted_at > expires_at then 'posted_at'
        end as error_column

    from {{ ref('posts') }} 
    where is_valid = 'INVALID'
)
select * from base