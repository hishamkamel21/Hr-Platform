with base as ( 
    select 
        payroll_id,
        employee_id,
        payment_date,
        bonus,
        deductions,
        tax, 
        salary,
        net_salary,
        created_at ,
        updated_at ,
        ingest_at ,
        
        case 
            when payroll_id is null 
              or employee_id is null 
              or net_salary is null 
              or salary is null 
               then 'NULL_ERROR'

            when net_salary < 0 
             or salary < 0 
              then 'OUTLIER_ERROR'

            when payment_date > current_date() 
               then 'FUTURE_DATE_ERROR'
        end as error_type,

        case 
            when payroll_id is null then 'payroll_id'
            when employee_id is null then 'employee_id'
            when salary is null or salary < 0 then 'salary'
            when net_salary is null or net_salary < 0 then 'net_salary'
            when payment_date > current_date() then 'payment_date'
        end as error_column

    from {{ ref('payrolls') }} 
    where is_valid = 'INVALID'
)
select * 
from base