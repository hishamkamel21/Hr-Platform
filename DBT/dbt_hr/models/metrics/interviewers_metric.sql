with base as ( 
    select 
    interviewer_id ,
    count(distinct interview_id) as total_interviews ,
    count_if(result = 'PASS') as total_passed_interviews ,
    count_if(result = 'FAIL') as total_failed_interviews ,
    count_if(result = 'PENDING') as total_pended_interviews ,
    min(interview_date) as first_interview ,
    max(interview_date) as last_interview ,
    avg(score) as avg_score_given 

    from {{ref('fact_interviews')}} 
    group by interviewer_id  
),
interviewer_applications as (
    select distinct
    iv.interviewer_id,
    a.candidate_id,
    a.job_id
    from {{ref('fact_interviews')}} iv
    left join {{ref('dim_applications')}} a 
    on iv.application_id = a.application_id
),
detect_hired as ( 
    select 
    ia.interviewer_id ,
    case 
      when h.candidate_id is not null then 1 
      else 0 
    end as is_hired 

    from interviewer_applications ia 
    left join {{ref('fact_hiring')}} h 
    on ia.candidate_id = h.candidate_id 
    and ia.job_id = h.job_id
),
hired_metric as ( 
    select 
    interviewer_id ,
    sum(is_hired) as total_hired 

    from detect_hired 
    group by interviewer_id
),
joined as ( 
    select 
    iv.* ,
    coalesce(h.total_hired, 0) as total_hired , 
    
    round(
        coalesce(h.total_hired, 0)::float / iv.total_interviews , 
        2
    ) * 100 as hired_prec ,

    round(
        iv.total_passed_interviews::float / iv.total_interviews ,
        2
    ) * 100 as pass_prec ,

    round(
        iv.total_failed_interviews::float / iv.total_interviews ,
        2
    ) * 100 as fail_prec  

    from base iv 
    left join hired_metric h 
    on iv.interviewer_id = h.interviewer_id
)
select * 
from joined 
