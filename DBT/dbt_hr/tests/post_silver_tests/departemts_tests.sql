
select * 
from {{ref('departments')}}
where is_valid = 'VALID'
AND(
    department_id is null 
    or department_name is null 
    or manager_id is null 
)