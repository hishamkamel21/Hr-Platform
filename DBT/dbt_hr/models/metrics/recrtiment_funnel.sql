-- CTE 1: Extract and clean job posting metadata (source platforms, post dates, and expiration dates)
with all_posts as ( 
    select 
        job_id,
        post_id,
        to_date(posted_at) as posted_at,   -- Truncate timestamp to date format for posting start
        to_date(expires_at) as expires_at, -- Truncate timestamp to date format for posting end
        platform as source                 -- Source channel/platform where the job was advertised (e.g., LinkedIn, Indeed)

    from {{ ref('dim_posts') }}
),

-- CTE 2: Join job applications (1:N join; fans out postings to individual candidate submissions)
all_applications as ( 
    select 
        p.*,
        a.application_id

    from all_posts p 
    left join {{ ref('dim_applications') }} a 
        on p.post_id = a.post_id  
),

-- CTE 3: Join interview facts (1:N join; fans out applications to individual interview rounds)
all_interviews as (
    select
        a.*,
        fi.interview_id

    from all_applications a 
    left join {{ ref('fact_interviews') }} fi 
        on a.application_id = fi.application_id
),

-- CTE 4: Join offer facts to track candidates reaching the offer stage
all_offers as ( 
    select 
        iv.*,
        fo.offer_id 

    from all_interviews iv 
    left join {{ ref('fact_offers') }} fo 
        on iv.application_id = fo.application_id
),

-- CTE 5: Join successful hiring facts to identify candidates who accepted and were onboarded
all_hired as ( 
    select 
        af.*,
        fh.application_id as hired_application 

    from all_offers af
    left join {{ ref('fact_hiring') }} fh 
        on af.application_id = fh.application_id
),

-- CTE 6: Aggregate metrics per job and posting channel to build the complete hiring funnel
funnel as ( 
    select 
        job_id,
        source, 
        min(posted_at) as posted_at,                  -- Earliest date the job was published on this channel
        max(expires_at) as expires_at,                -- Latest date the posting remained active on this channel
        count(application_id) as total_applications,   -- Total candidates who applied through this channel
        
        -- Total interviews conducted from applications via this channel
        count_if(
            interview_id is not null 
        ) as total_interviews,

        -- Total job offers extended to applicants from this channel
        count_if(
            offer_id is not null 
        ) as total_offers,

        -- Total successful hires converted from this channel
        count_if(
            hired_application is not null 
        ) as total_hired 

    from all_hired 
    group by job_id, source 
)

-- Final Output: Recruitment sourcing channel efficiency and conversion funnel report
select * 
from funnel