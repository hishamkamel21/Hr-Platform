{{
    config(
        materialized="incremental",
        unique_key="job_id",
        incremental_strategy="merge",
        on_schema_change="append_new_columns"
    )
}}

with base as ( 
    select 
        {{ handle_Ids('job_id') }} as job_id,
        upper(trim(job_department)) as department_name,
        lower(trim(job_title)) as job_title,
        lower(trim(job_level)) as job_level, 
        {{ clean_salary('min_salary') }} as min_salary,
        {{ clean_salary('max_salary') }} as max_salary,
        created_at,
        updated_at,
        ingest_at
    from {{ source('bronze', 'jobs') }} 
    
    {% if is_incremental() %}
        where updated_at > (
            select coalesce(max(updated_at), '1900-01-01')
            from {{ this }}
        )
    {% endif %}
),

stage as ( 
    select 
        j.job_id,
        j.department_name, 
        j.job_title,
        j.job_level,
        j.min_salary,
        j.max_salary,
        j.created_at,
        j.updated_at,
        j.ingest_at,
        d.department_id,
        case 
          when d.department_id is null then 1 
          else 0 
        end as need_parse 
    from base j 
    left join {{ ref('departments') }} d 
        on j.department_name = d.department_name
    qualify row_number() over(
        partition by j.job_id 
        order by j.updated_at desc
    ) = 1
),

need_parse as ( 
    select 
        s.job_id,
        s.department_name, 
        s.job_title,
        s.job_level,
        s.min_salary,
        s.max_salary,
        s.created_at,
        s.updated_at,
        s.ingest_at
    from stage s 
    where s.need_parse = 1 
),

dont_need_parse as ( 
    select 
        s.job_id,
        s.department_id, 
        s.job_title,
        s.job_level,
        s.min_salary,
        s.max_salary,
        s.created_at,
        s.updated_at,
        s.ingest_at 
    from stage s 
    where s.need_parse = 0
),

parsed as ( 
    select 
        j.job_id, 
        dp.department_name, 
        j.job_title,
        j.job_level,
        j.min_salary,
        j.max_salary,
        j.created_at,
        j.updated_at,
        j.ingest_at 
    from need_parse j 
    left join {{ ref('departments_patterns') }} dp 
        on j.department_name rlike dp.pattern 
    qualify row_number() over (
        partition by j.job_id 
        order by dp.piriorty asc 
    ) = 1 
),

joined as ( 
    select 
        j.job_id,
        d.department_id, 
        j.job_title,
        j.job_level,
        j.min_salary,
        j.max_salary,
        j.created_at,
        j.updated_at,
        j.ingest_at
    from parsed j 
    left join {{ ref('departments') }} d 
        on j.department_name = d.department_name 
)

select * from joined 
union all 
select * from dont_need_parse