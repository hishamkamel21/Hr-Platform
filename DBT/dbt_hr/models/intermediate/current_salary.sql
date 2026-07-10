with current_payrolls as ( 
    select
        employee_id,
        payment_date,
        salary as month_salary 
    from {{ ref('payrolls') }} 
    where is_valid = 'VALID'
)

select
    employee_id,
    payment_date,
    month_salary
from current_payrolls 
qualify row_number() over(
    partition by employee_id
    order by payment_date desc
) = 1