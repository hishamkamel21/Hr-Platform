
select * 
from {{ref('seprations')}}
where is_valid = 'VALID'
AND ( 
    employee_id is null 
    or type is null 
    or reason is null 
    or last_working_day is null 
    or last_working_day > current_date()
) 
