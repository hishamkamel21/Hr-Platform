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
    offer_id , 
    application_id ,
    job_id ,
    candidate_id ,
    offered_salary ,
    offer_date ,
    expire_date ,
    acceptance_date ,
    created_at ,
    updated_at ,
    ingest_at ,
    case 
      when acceptance_date is not null 
      then 1 
      else 0 
    end as is_hired 

    from {{ref('offers')}}

    where is_valid = 'VALID'
    {% if is_incremental() %}
        AND updated_at >
        (
            SELECT COALESCE(MAX(updated_at), '1900-01-01')
            FROM {{ this }}
        )
    {% endif %}
 
)
select * 
from base 
