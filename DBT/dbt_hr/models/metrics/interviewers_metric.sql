-- CTE 1: Aggregate interviewer activity, outcome distribution, evaluation scores, and activity range
with base as ( 
    select 
        interviewer_id,
        count(distinct interview_id) as total_interviews,
        count_if(result = 'PASS') as total_passed_interviews,
        count_if(result = 'FAIL') as total_failed_interviews,
        count_if(result = 'PENDING') as total_pended_interviews,
        min(interview_date) as first_interview, -- Earliest date this interviewer conducted an interview
        max(interview_date) as last_interview,  -- Most recent date this interviewer conducted an interview
        avg(score) as avg_score_given            -- Mean evaluation score assigned across all interviews

    from {{ ref('fact_interviews') }} 
    group by interviewer_id  
),

-- CTE 2: Map unique interviewer to candidate and job combinations evaluated
interviewer_applications as (
    select distinct
        iv.interviewer_id,
        a.candidate_id,
        a.job_id

    from {{ ref('fact_interviews') }} iv
    left join {{ ref('dim_applications') }} a 
        on iv.application_id = a.application_id
),

-- CTE 3: Flag candidates evaluated by each interviewer who ultimately got hired for the specific job
detect_hired as ( 
    select 
        ia.interviewer_id,
        case 
            when h.candidate_id is not null then 1 
            else 0 
        end as is_hired 

    from interviewer_applications ia 
    left join {{ ref('fact_hiring') }} h 
        on ia.candidate_id = h.candidate_id 
        and ia.job_id = h.job_id
),

-- CTE 4: Calculate total successful hires attributed to candidates each interviewer evaluated
hired_metric as ( 
    select 
        interviewer_id,
        sum(is_hired) as total_hired 

    from detect_hired 
    group by interviewer_id
),

-- CTE 5: Combine interviewer interview counts with hiring metrics and calculate conversion efficiency percentages
joined as ( 
    select 
        iv.*,
        coalesce(h.total_hired, 0) as total_hired, 
        
        -- Percentage of interviews that resulted in a successful hire
        round(
            coalesce(h.total_hired, 0)::float / nullif(iv.total_interviews, 0), 
            2
        ) * 100 as hired_prec,

        -- Percentage of interviews passed by the interviewer
        round(
            iv.total_passed_interviews::float / nullif(iv.total_interviews, 0),
            2
        ) * 100 as pass_prec,

        -- Percentage of interviews failed by the interviewer
        round(
            iv.total_failed_interviews::float / nullif(iv.total_interviews, 0),
            2
        ) * 100 as fail_prec  

    from base iv 
    left join hired_metric h 
        on iv.interviewer_id = h.interviewer_id
)

-- Final Output: Return detailed interviewer performance, pass/fail distribution, and hiring conversion metrics
select * 
from joined