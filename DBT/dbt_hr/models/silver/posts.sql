{{
    config(
        materialized="incremental",
        unique_key="post_id",
        incremental_strategy="merge",
        on_schema_change = "append_new_columns"
    )
}}
with base as ( 
    select 
    {{ handle_Ids('post_id')}} as post_id ,
    {{ handle_Ids('job_id')}} as job_id,
    {{ handle_Ids('posted_by')}} as posted_by,
    case 
      when platform is null 
       then null 
      when upper(trim(platform)) = '' 
       then null
      else upper(trim(platform))
    end as platform,
    to_timestamp(posted_at) as posted_at,
    to_timestamp(expires_at) as expires_at,
    created_at , 
    updated_at ,
    ingest_at

    from {{source('bronze','posts')}} 

    {% if is_incremental() %}
        where updated_at >
        (
            SELECT COALESCE(MAX(updated_at), '1900-01-01')
            FROM {{ this }}
        )
    {% endif %}

),
stage as ( 
    select
    * ,
    {{ foreign_key_check(
        main = 'p',
        ref_model = 'jobs',
        foreign_key = 'job_id',
        add_ref_validity = TRUE ,
        alias = 'foreign_job_error'
    )}},

    {{ foreign_key_check(
        main = 'p',
        ref_model = 'employees',
        foreign_key = 'posted_by',
        add_ref_validity = TRUE ,
        ref_foreign_key = 'employee_id',
        alias = 'foreign_employee_error'
    )}}

    from base p 
    qualify row_number() over (
        partition by p.post_id 
        order by p.updated_at desc 
    ) = 1 
)
select
* ,
case 
  when post_id is null 
    or job_id is null 
    or posted_by is null 
    or platform is null 
    or foreign_job_error = 1 
    or foreign_employee_error = 1  
    or posted_at is null 
    or posted_at > current_timestamp() 
    or posted_at > expires_at 
  then 'INVALID'
  else 'VALID'
end as is_valid

from stage