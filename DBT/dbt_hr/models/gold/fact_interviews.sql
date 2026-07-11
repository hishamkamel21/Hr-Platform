{{
    config(
        materialized="incremental",
        unique_key="interview_id",
        incremental_strategy="merge",
        on_schema_change = "append_new_columns"
    )
}}

with base as ( 
    select 
    interview_id ,
    application_id ,
    interviewer_id ,
    interview_stage ,
    interview_date ,
    interview_timestamp ,
    score ,
    result ,
    created_at ,
    updated_at ,
    ingest_at
    from {{ref('interviews')}} 
    where is_valid = 'VALID' 
    {% if is_incremental() %}
        AND updated_at >
        (
            SELECT COALESCE(MAX(updated_at), '1900-01-01')
            FROM {{ this }}
        )
    {% endif %}
)
SELECT * 
FROM base 