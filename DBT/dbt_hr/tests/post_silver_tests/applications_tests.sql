
SELECT * 
FROM {{ref('applications')}} 
WHERE is_valid = 'VALID' 
AND (
    application_id IS NULL 
    OR job_id IS NULL 
    OR candidate_id IS NULL 
    OR post_id IS NULL  
    OR application_date is null 
    OR application_date > current_date()
)
