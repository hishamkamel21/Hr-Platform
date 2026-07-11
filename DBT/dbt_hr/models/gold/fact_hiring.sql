with base as ( 
    select 
    offer_id ,
    application_id ,
    job_id ,
    candidate_id ,
    offered_salary as accepeted_salary , 
    acceptance_date

    from {{ref('fact_offers')}} 
    where is_hired = 1  

    {% if is_incremental() %}
        and updated_at >
        (
            SELECT COALESCE(MAX(procssed_at), '1900-01-01')
            FROM {{ this }}
        )
    {% endif %}
),
detect_apply_date as ( 
    select 
    h.* ,
    a.application_timestamp 

    from base h 
    left join {{ref('dim_applications')}} a 
    on h.application_id = a.application_id 
),
join_with_interviews as ( 
    select 
    h.* ,
    iv.interview_id ,
    iv.score 

    from detect_apply_date h 
    left join {{ref('fact_interviews')}} iv 
    on h.application_id = iv.application_id
),
hire_metric as ( 
    select  
    candidate_id ,
    job_id , 
    application_id ,
    count(distinct interview_id) as total_interviews ,
    avg(score) as avg_score ,
    max(accepeted_salary) as accepeted_salary ,
    max(acceptance_date) as accepeted_date ,
    max(application_timestamp) as apply_date 
    
    from join_with_interviews
    group by candidate_id , job_id , application_id
),
salary_metric as ( 
    select 
    h.* , 
     round(
        (h.accepeted_salary - j.min_salary) / (j.max_salary - j.min_salary) ,
        2
    ) as accepeted_salary_position ,

    j.max_salary - h.accepeted_salary as salary_gap ,

    case 
      when h.accepeted_salary < j.min_salary 
       then 'Under_Paid'
      when h.accepeted_salary > j.max_salary 
       then 'Over_Paid'
      else 'Within_range' 
    end as pay_flag , 
    

    round (
        h.accepeted_salary / j.max_salary ,
        2
    ) as Offer_Competitiveness_Ratio


    from hire_metric h 
    left join {{ref('job_history')}} j 
    on h.job_id = j.job_id 
    and h.accepeted_date between j.dbt_valid_from and coalesce(j.dbt_valid_to,current_timestamp())
)
select 
* , 
datediff(
    day, apply_date, accepeted_date 
) as time_to_hire ,

current_timestamp() as procssed_at 

from salary_metric 
