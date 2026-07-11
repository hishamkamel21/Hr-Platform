{{
    config(
        materialized="incremental",
        unique_key="payroll_id",
        incremental_strategy="merge",
        on_schema_change="append_new_columns"
    )
}}

with base as ( 
    select  
        {{ handle_Ids('payroll_id') }} as payroll_id,
        {{ handle_Ids('employee_id') }} as employee_id,
        {{ fix_date_formats('payment_date') }} as payment_date,
        {{ clean_salary('salary') }} as salary,
        cast(coalesce(bouns, 0.0) as double) as bonus, 
        cast(coalesce(deductions, 0.0) as double) as deductions,
        try_cast(tax as double) as tax,
        {{ clean_salary('net_salary') }} as net_salary,
        created_at,
        updated_at,
        ingest_at 
    from {{ source('bronze', 'payrolls') }}
       
    {% if is_incremental() %}
        where updated_at > (
            select coalesce(max(updated_at), '1900-01-01')
            from {{ this }}
        )
    {% endif %}
),

flagged as (
    select 
        *, 
        case 
            when (salary < 0 or salary is null) and (net_salary is not null or net_salary > 0) then 'can_fix'
            when (salary < 0 or salary is null) and (net_salary is null or net_salary <= 0) then 'can_not_fix'
            else 'valid' 
        end as salary_flag, 

        case 
            when (net_salary < 0 or net_salary is null) and (salary is not null or salary > 0) then 'can_fix'
            when (net_salary < 0 or net_salary is null) and (salary is null or salary <= 0) then 'can_not_fix' 
            else 'valid'
        end as net_salary_flag 
    from base p 
    qualify row_number() over(
        partition by p.payroll_id 
        order by p.updated_at desc
    ) = 1 
),

final as ( 
    select 
        payroll_id,
        employee_id,
        payment_date,
        bonus, 
        deductions,
        tax, 
        case 
            when salary_flag = 'can_fix' then (net_salary + deductions + tax) - bonus
            else salary 
        end as salary, 

        case 
            when net_salary_flag = 'can_fix' then ((salary + bonus) - (deductions + tax)) 
            else net_salary 
        end as net_salary,
      
        created_at,
        updated_at,
        ingest_at,
        case 
            when payroll_id is null or 
                 employee_id is null or 
                 salary_flag = 'can_not_fix' or 
                 net_salary_flag = 'can_not_fix' or 
                 payment_date > current_date() then 'INVALID'
            else 'VALID' 
        end as is_valid
    from flagged 
)

select * 
from final