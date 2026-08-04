-- Model Configuration Block: Defines dbt materialization settings and merge behavior
{{
    config(
        materialized="incremental",
        unique_key="job_id",
        incremental_strategy="merge",
        on_schema_change="append_new_columns"
    )
}}

-- CTE 1: Extract raw job records, apply formatting macros, and filter for new/updated data during incremental runs
with base as ( 
    select 
        {{ handle_Ids('job_id') }} as job_id,             -- Custom macro to sanitize and format job unique identifiers
        upper(trim(job_department)) as department_name,  -- Standardize department name for exact matching
        lower(trim(job_title)) as job_title,              -- Standardize job titles to lowercase
        lower(trim(job_level)) as job_level,              -- Standardize job seniority levels
        {{ clean_salary('min_salary') }} as min_salary,  -- Custom macro to sanitize and cast minimum salary values
        {{ clean_salary('max_salary') }} as max_salary,  -- Custom macro to sanitize and cast maximum salary values
        created_at,
        updated_at,
        ingest_at
    from {{ source('bronze', 'jobs') }} 
    
    -- dbt Incremental Block: Filters source records modified since the latest updated_at timestamp in target table
    {% if is_incremental() %}
        where updated_at > (
            select coalesce(max(updated_at), '1900-01-01')
            from {{ this }}
        )
    {% endif %}
),

-- CTE 2: Match raw departments against standardized department reference model and deduplicate per job_id
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
        
        -- Flag records requiring fuzzy pattern matching (1 = unmatched department, 0 = direct match found)
        case 
            when d.department_id is null then 1 
            else 0 
        end as need_parse 
    from base j 
    left join {{ ref('departments') }} d 
        on j.department_name = d.department_name

    -- Deduplicate base records: keep only the most recently updated entry per job_id
    qualify row_number() over(
        partition by j.job_id 
        order by j.updated_at desc
    ) = 1
),

-- CTE 3: Isolate records that failed direct department lookup and require regex parsing
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

-- CTE 4: Isolate records that matched directly to existing departments (bypasses pattern parsing)
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

-- CTE 5: Map unmapped departments using regex pattern rules; resolve multi-matches by pattern priority ranking
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

    -- Priority disambiguation: Pick the highest priority rule when department matches multiple patterns
    qualify row_number() over (
        partition by j.job_id 
        order by dp.piriorty asc 
    ) = 1 
),

-- CTE 6: Re-join parsed department names back to the standardized departments table to fetch department_id
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

-- Final Output: Combine directly mapped departments with newly pattern-parsed department records
select * from joined 
union all 
select * from dont_need_parse