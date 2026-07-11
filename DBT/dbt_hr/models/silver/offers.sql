 {{
    config(
        materialized="incremental",
        unique_key="offer_id",
        incremental_strategy="merge",
        on_schema_change = "append_new_columns"
    )
}}

with base as ( 
    select 

    {{ handle_Ids('offer_id') }} as offer_id ,
    {{ handle_Ids('application_id') }} as application_id ,
    {{ handle_Ids('job_id') }} as job_id, 
    {{ handle_Ids('candidate_id') }} as candidate_id,
    {{ clean_salary('offered_salary')}} as offered_salary, 
    to_timestamp(offer_date) as offer_date ,
    to_timestamp(expire_date) as expire_date ,

    case 
      when acceptance_date is not null 
      then to_timestamp(acceptance_date)
      else NULL 
    end as acceptance_date ,

    created_at ,
    updated_at,
    ingest_at

    from {{source('bronze','offers')}} 

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
    o.* ,

    {{ foreign_key_check(
        main = 'o' , 
        ref_model = 'applications' ,
        foreign_key = 'application_id',
        add_ref_validity = TRUE ,
        alias = 'foreign_application_error'
    ) }} ,

    {{ foreign_key_check(
        main = 'o',
        ref_model = 'jobs',
        foreign_key = 'job_id',
        add_ref_validity = TRUE ,
        alias = 'foreign_job_error'
    ) }} ,

    {{ foreign_key_check(
        main = 'o' ,
        ref_model = 'candidates',
        foreign_key = 'candidate_id',
        add_ref_validity = TRUE ,
        alias = 'foreign_candidate_error'
    ) }}
    
    from base o

    qualify row_number() over ( 
        partition by o.offer_id 
        order by o.created_at 
    ) = 1 
),
final as ( 
    select 

    offer_id,
    application_id,
    job_id,
    candidate_id,
    offered_salary,
    offer_date,
    expire_date,
    acceptance_date,
    created_at ,
    updated_at ,
    ingest_at ,
    foreign_application_error ,
    foreign_job_error ,
    foreign_candidate_error ,

    case 
      when foreign_candidate_error = 1 or 
         foreign_job_error = 1 or
         foreign_application_error = 1 or
         job_id is null or 
         application_id is null or 
         candidate_id is null or 
         offer_date > current_date() or 
         offer_id is null or
         offered_salary < 0 
      then 'INVALID'
      else 'VALID'
    end as is_valid 

    from stage
)

select *
from final 