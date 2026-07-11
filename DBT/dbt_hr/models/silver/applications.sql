
{{
    config(
        materialized="incremental",
        unique_key="application_id",
        incremental_strategy="merge",
        on_schema_change = "append_new_columns"
    )
}}

with base as ( 
    select 
    {{ handle_Ids('application_id') }} as application_id,
    {{ handle_Ids('candidate_id') }} as candidate_id,
    {{ handle_Ids('job_id') }} as job_id ,
    {{ handle_Ids('post_id') }} as post_id ,
    to_timestamp(application_date) as application_timestamp ,
    to_date(application_date) as application_date,
    coalesce(upper(trim(source)) , 'N/A') as source ,
    created_at ,
    updated_at ,
    ingest_at

    from {{source('bronze','applications')}} 
    {% if is_incremental() %}
        WHERE updated_at >
        (
            SELECT COALESCE(MAX(updated_at), '1900-01-01')
            FROM {{ this }}
        )
    {% endif %}

),
stage as ( 
    select 
    a.* ,
    {{ foreign_key_check(
        main = 'a',
        ref_model = 'candidates',
        add_ref_validity = TRUE ,
        foreign_key = 'candidate_id',
        alias = 'foreign_candidate_error'
    ) }} ,

    {{ foreign_key_check(
        main = 'a' ,
        ref_model = 'jobs' ,
        add_ref_validity = TRUE ,
        foreign_key = 'job_id' ,
        alias = 'foreign_job_error'
    ) }} ,

    {{ foreign_key_check(
        main = 'a',
        ref_model ='posts',
        add_ref_validity = TRUE,
        foreign_key ='post_id',
        alias = 'foreign_post_error'
    )}}

    from base a 
    qualify row_number() over(
        partition by a.application_id
        order by a.updated_at desc 
    ) = 1 
)
SELECT  
* ,
CASE 
  WHEN application_id is null 
  or candidate_id is null 
  or job_id is null 
  or post_id is null 
  or application_date is null  
  or foreign_candidate_error = 1 
  or foreign_job_error = 1 
  or foreign_post_error = 1 
  or application_date > current_date()
  then 'INVALID'
  else 'VALID'
end as is_valid 

from stage  
  
