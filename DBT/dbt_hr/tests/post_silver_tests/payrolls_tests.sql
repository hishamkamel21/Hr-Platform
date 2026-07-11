SELECT *
FROM {{ref('payrolls')}} 
WHERE is_valid = 'VALID'
AND ( 
    payroll_id IS NULL 
    OR employee_id IS NULL 
    OR salary IS NULL 
    OR salary < 0 
    OR net_salary IS NULL 
    OR net_salary < 0 
    OR payment_date > current_date()
)

