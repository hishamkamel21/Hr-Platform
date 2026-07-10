
select * 
from {{ref('interviews')}}
where is_valid = 'VALID'
AND ( 
    interview_id is null 
    or application_id is null 
    or interviewer_id is null 
    or result is null 
    or interview_date is null 
    or interview_date > current_date()
)

