
with base as ( 
    select 
    application_id ,
    candidate_id ,
    job_id , 
    post_id ,
    application_date ,
    source ,
    created_at ,
    updated_at ,
    ingest_at ,
    CASE 
      when application_id is null 
        or candidate_id is null 
        or job_id  is null 
        or post_id is null
        or application_date is null  
      then 'NULL_ERROR' 

      when foreign_candidate_error = 1 
        or foreign_job_error = 1 
        or foreign_post_error = 1 
      then 'FOREIGN_KEY_ERROR' 

      when application_date > current_date()
      then 'FUTURE_DATE_ERROR' 
    END AS Error_Type ,


    CASE 
      when application_id is null 
        then 'Application_id' 
      when candidate_id is null 
       or foreign_candidate_error = 1 
        then 'Candidate_id' 
      when post_id is null 
       or foreign_post_error = 1 
        then 'Post_id'
      when job_id is null 
       or foreign_job_error = 1 
        then 'Job_id'
      when application_date is null 
       or application_date > current_date() 
        then 'Application_date' 
    END AS Error_Column 
    
    from {{ref('applications')}} 
    where is_valid = 'INVALID'
)
select * 
from base 