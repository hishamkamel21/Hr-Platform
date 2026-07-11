
select * 
from {{ref('posts')}} 
where is_valid = 'VALID'
AND (
    post_id is null 
    or job_id is null 
    or posted_by is null 
    or platform is null 
    or posted_at is null 
    or posted_at > current_timestamp()
    or posted_at > expires_at 
) 

