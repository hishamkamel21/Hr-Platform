with base as ( 
    select 
        offer_id,
        application_id,
        job_id,
        candidate_id,
        offered_salary,
        offer_date,
        expire_date,
        created_at,
        updated_at ,
        ingest_at,
        
        case 
            when offer_id is null 
              or application_id is null 
              or job_id is null 
              or candidate_id is null 
               then 'NULL_ERROR'
            when foreign_application_error = 1 
              or foreign_job_error = 1 
              or foreign_candidate_error = 1 
               then 'FOREIGN_KEY_ERROR'
            when offer_date > current_date() 
              or acceptance_date > current_date() 
               then 'FUTURE_DATE_ERROR'
            when offered_salary < 0 
               then 'VALUE_ERROR'
        end as error_type,

        case 
            when offer_id is null then 'offer_id'
            when application_id is null or foreign_application_error = 1 then 'application_id'
            when job_id is null or foreign_job_error = 1 then 'job_id'
            when candidate_id is null or foreign_candidate_error = 1 then 'candidate_id'
            when offered_salary < 0 then 'offered_salary'
            when offer_date > current_date() then 'offer_date'
            when acceptance_date > current_date() then 'acceptance_date'
        end as error_column

    from {{ ref('offers') }} 
    where is_valid = 'invalid'
)
select * 
from base