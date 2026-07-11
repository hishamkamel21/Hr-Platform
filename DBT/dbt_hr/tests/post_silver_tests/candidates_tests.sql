
select * 
from {{ref('candidates')}} 
where is_valid = 'VALID'
AND candidate_id is null  
