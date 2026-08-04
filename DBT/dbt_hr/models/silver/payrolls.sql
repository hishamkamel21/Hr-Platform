-- Model Configuration Block: Defines incremental materialization, merge updates on payroll_id, and auto-appends new schema columns
{{
    config(
        materialized="incremental",
        unique_key="payroll_id",
        incremental_strategy="merge",
        on_schema_change="append_new_columns"
    )
}}

-- CTE 1: Extract bronze raw payroll records, sanitize field formats/types, handle null adjustments, and apply incremental filter
with base as ( 
    select  
        {{ handle_Ids('payroll_id') }} as payroll_id,        -- Standardize and clean payroll unique primary key
        {{ handle_Ids('employee_id') }} as employee_id,      -- Standardize and clean employee foreign key
        {{ fix_date_formats('payment_date') }} as payment_date, -- Convert payment date string into unified date type
        {{ clean_salary('salary') }} as salary,              -- Sanitize and cast base gross salary
        cast(coalesce(bouns, 0.0) as double) as bonus,       -- Default missing bonus values to 0.0 (preserves source column name 'bouns')
        cast(coalesce(deductions, 0.0) as double) as deductions, -- Default missing deductions to 0.0
        try_cast(tax as double) as tax,                      -- Safely cast tax amount; returns NULL on non-numeric formats
        {{ clean_salary('net_salary') }} as net_salary,      -- Sanitize and cast net take-home pay
        created_at,
        updated_at,
        ingest_at 
    from {{ source('bronze', 'payrolls') }}
        
    -- dbt Incremental Block: Filters source records modified since the max updated_at in the target table
    {% if is_incremental() %}
        where updated_at > (
            select coalesce(max(updated_at), '1900-01-01')
            from {{ this }}
        )
    {% endif %}
),

-- CTE 2: Deduplicate records by payroll_id and assign fixability status flags for gross and net salary anomalies
flagged as (
    select 
        *, 
        -- Classify Gross Salary validity and repairability based on available Net Salary
        case 
            when (salary < 0 or salary is null) and (net_salary is not null or net_salary > 0) then 'can_fix'
            when (salary < 0 or salary is null) and (net_salary is null or net_salary <= 0) then 'can_not_fix'
            else 'valid' 
        end as salary_flag, 

        -- Classify Net Salary validity and repairability based on available Gross Salary
        case 
            when (net_salary < 0 or net_salary is null) and (salary is not null or salary > 0) then 'can_fix'
            when (net_salary < 0 or net_salary is null) and (salary is null or salary <= 0) then 'can_not_fix' 
            else 'valid'
        end as net_salary_flag 
    from base p 

    -- Deduplicate base rows: retain only the latest record state per payroll_id
    qualify row_number() over(
        partition by p.payroll_id 
        order by p.updated_at desc
    ) = 1 
),

-- CTE 3: Reconstruct missing salary components using accounting formulas and assign row-level validation status
final as ( 
    select 
        payroll_id,
        employee_id,
        payment_date,
        bonus, 
        deductions,
        tax, 

        -- Reconstruct Gross Salary if fixable: Gross = (Net Salary + Deductions + Tax) - Bonus
        case 
            when salary_flag = 'can_fix' then (net_salary + deductions + tax) - bonus
            else salary 
        end as salary, 

        -- Reconstruct Net Salary if fixable: Net = (Gross Salary + Bonus) - (Deductions + Tax)
        case 
            when net_salary_flag = 'can_fix' then ((salary + bonus) - (deductions + tax)) 
            else net_salary 
        end as net_salary,
      
        created_at,
        updated_at,
        ingest_at,

        -- Assign overall data quality status based on critical primary keys, unfixable errors, or future payment dates
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

-- Final Output: Return cleansed, backfilled, and audit-flagged payroll data
select * 
from final