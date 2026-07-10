with base as ( 
    select 
    interview_id ,
    application_id ,
    interviewer_id ,
    interview_stage ,
    interview_date ,
    score , 
    result ,
    created_at ,
    updated_at,
    ingest_at ,
    case 
      when interview_id is null 
       or application_id is null 
       or interviewer_id is null 
       or result is null 
        then 'NULL_ERROR'
       when foreign_application_error = 1 
        or foreign_employee_error = 1 
         then 'FOREIGN_KEY_ERROR'
       when interview_date > current_date() 
         then 'FUTURE_DATE_ERROR'
    end as Error_Type ,

    case 
      when interview_id is null 
       then 'interview_id'
      when application_id is null 
        or foreign_application_error = 1 
         then 'application_id'
      when interviewer_id is null 
        or foreign_employee_error = 1 
         then 'interviewer_id' 
      when result is null 
       then 'result'
      when interview_date > current_date()
       then 'interview_date'
    end as Error_Column
      
    from {{ref('interviews')}} 
    where is_valid = 'INVALID'
)
select * 
from base 