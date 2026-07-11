SELECT * 
FROM {{ ref('offers') }} 
WHERE is_valid = 'VALID' 
  AND (
     offer_id IS NULL 
     OR job_id IS NULL 
     OR application_id IS NULL
     OR candidate_id IS NULL
     OR offered_salary < 0 
     OR offer_date > CURRENT_DATE() 
  )
