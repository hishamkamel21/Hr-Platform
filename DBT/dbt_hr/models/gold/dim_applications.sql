
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
    application_id ,
    candidate_id ,
    job_id ,
    post_id ,
    application_timestamp ,
    application_date ,
    source ,
    created_at ,
    updated_at ,
    ingest_at 
    
    from {{ref('applications')}} 
    where is_valid = 'VALID'
    {% if is_incremental() %}
        and updated_at >
        (
            SELECT COALESCE(MAX(updated_at), '1900-01-01')
            FROM {{ this }}
        )
    {% endif %}

)
select *
from base 