with metric as ( 
    select 
    department_id ,
    DATE_TRUNC('year', payment_date) as payment_year , 
    sum(salary) as sum_salary ,
    sum(bonus) as sum_bouns , 
    sum(deductions) as sum_deductions ,
    round(avg(salary),2) as avg_salary ,
    round(avg(bonus),2) as avg_bouns ,
    round(avg(deductions),2) as avg_deductions 

    from {{ref('fact_payrolls')}} 
    group by department_id , DATE_TRUNC('year', payment_date) 
),
total as ( 
    select 
     DATE_TRUNC('year', payment_date) as payment_year , 
     sum(salary) as total_salary ,
     sum(bonus) as total_bouns ,
     sum(deductions) as total_deductions

    from {{ref('fact_payrolls')}}
    group by DATE_TRUNC('year', payment_date) 
),
final as ( 
    select 
    m.* ,

    round(
        m.sum_salary::float / nullif(t.total_salary, 0),
        2
    ) * 100 as salary_pct_share ,

    round(
        m.sum_bouns::float / nullif(t.total_bouns, 0) ,
        2
    ) * 100 as bouns_pct_share,

    round(
        m.sum_deductions::float / nullif(t.total_deductions, 0) ,
        2
    ) * 100 as deductions_pct_share 

    from metric m 
    left join total t 
    on m.payment_year = t.payment_year
)
select * 
from final 
