{{
    config(
        materialized="incremental",
        unique_key="candidate_id",
        incremental_strategy="merge",
        on_schema_change = "append_new_columns"
    )
}}

with base as ( 
    select 
    candidate_id ,
    full_name ,
    email ,
    phone ,
    created_at ,
    updated_at ,
    ingest_at
    from {{ref('candidates')}}
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