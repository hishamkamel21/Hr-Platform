
with all_posts as ( 
    select 
    job_id , post_id , to_date(posted_at) as posted_at , to_date(expires_at) as expires_at , platform as source 
    from {{ref('dim_posts')}}
),
all_applications as ( 
    select 
    p.* ,
    a.application_id

    from all_posts p 
    left join {{ref('dim_applications')}} a 
    on p.post_id = a.post_id  
),
all_interviews as (
    select
    a.* ,
    fi.interview_id

    from all_applications a 
    left join {{ref('fact_interviews')}} fi 
    on a.application_id = fi.application_id
),
all_offers as ( 
    select 
    iv.* ,
    fo.offer_id 

    from all_interviews iv 
    left join {{ref('fact_offers')}} fo 
    on iv.application_id = fo.application_id
),
all_hired as ( 
    select 
    af.* ,
    fh.application_id as hired_application 

    from all_offers af
    left join {{ref('fact_hiring')}} fh 
    on af.application_id = fh.application_id
),
funnel as ( 
    select 
    job_id ,
    source , 
    min(posted_at) as posted_at ,
    max(expires_at) as expires_at ,
    count(application_id) as total_applications ,
    count_if(
        interview_id is not null 
    ) as total_interviews ,

    count_if(
        offer_id is not null 
    ) as total_offers ,

    count_if(
        hired_application is not null 
    ) as total_hired 


    from all_hired 
    group by job_id,source 
)
select * 
from funnel