-- CTE 1: Extract base hiring data with dbt incremental processing logic
with base as ( 
    select 
        offer_id,
        application_id,
        job_id,
        candidate_id,
        offered_salary as accepeted_salary, -- Maps accepted compensation
        acceptance_date

    from {{ ref('fact_offers') }} 
    where is_hired = 1 -- Filter exclusively for successful hires 

    -- dbt Incremental Materialization Hook: Filters for records updated since the last run
    {% if is_incremental() %}
        and updated_at > (
            select coalesce(max(procssed_at), '1900-01-01')
            from {{ this }}
        )
    {% endif %}
),

-- CTE 2: Join application metadata to track when the candidate originally applied
detect_apply_date as ( 
    select 
        h.*,
        a.application_timestamp 

    from base h 
    left join {{ ref('dim_applications') }} a 
        on h.application_id = a.application_id 
),

-- CTE 3: Join interview records (1:N relationship; expands rows per application)
join_with_interviews as ( 
    select 
        h.*,
        iv.interview_id,
        iv.score 

    from detect_apply_date h 
    left join {{ ref('fact_interviews') }} iv 
        on h.application_id = iv.application_id
),

-- CTE 4: Aggregate to 1 row per application; compute interview metrics and consolidate offer attributes
hire_metric as ( 
    select  
        candidate_id,
        job_id, 
        application_id,
        count(distinct interview_id) as total_interviews,
        avg(score) as avg_score,
        max(accepeted_salary) as accepeted_salary,
        max(acceptance_date) as accepeted_date,
        max(application_timestamp) as apply_date 
    
    from join_with_interviews
    group by candidate_id, job_id, application_id
),

-- CTE 5: Join job salary bands to calculate compensation metrics and pay compliance flags
salary_metric as ( 
    select 
        h.*, 
        -- Position within the job's salary range (0.00 = min, 1.00 = max)
        round(
            (h.accepeted_salary - j.min_salary) / nullif(j.max_salary - j.min_salary, 0),
            2
        ) as accepeted_salary_position,

        -- Headroom remaining before reaching the job maximum salary
        j.max_salary - h.accepeted_salary as salary_gap,

        -- Salary band compliance status relative to job market bounds
        case 
            when h.accepeted_salary < j.min_salary then 'Under_Paid'
            when h.accepeted_salary > j.max_salary then 'Over_Paid'
            else 'Within_range' 
        end as pay_flag, 

        -- Ratio of accepted salary against the maximum budget allocated for the role
        round(
            h.accepeted_salary / nullif(j.max_salary, 0),
            2
        ) as Offer_Competitiveness_Ratio

    from hire_metric h 
    left join {{ ref('dim_jobs') }} j 
        on h.job_id = j.job_id 
)

-- Final Output: Calculate recruitment cycle duration and append dbt execution timestamp
select 
    *, 
    -- Total time elapsed (in days) from application date to offer acceptance date
    datediff(
        day, apply_date, accepeted_date 
    ) as time_to_hire,

    -- Metadata tracking field used for incremental processing on future runs
    current_timestamp() as procssed_at 

from salary_metric