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
    {{ handle_Ids('candidate_id')}} as candidate_id,
    LOWER(TRIM(first_name)) as first_name ,
    LOWER(TRIM(last_name)) as last_name ,
    coalesce(email,'N/A') as email , 
    coalesce(phone,'N/A') as phone ,
    created_at ,
    updated_at , 
    ingest_at

    from {{source('bronze','candidates')}}  
    {% if is_incremental() %}
        WHERE updated_at >
        (
            SELECT COALESCE(MAX(updated_at), '1900-01-01')
            FROM {{ this }}
        )
    {% endif %}
)
select 
candidate_id ,
concat_ws(' ', first_name, last_name) as full_name,
email , 
phone ,
created_at ,
updated_at ,
ingest_at ,
case 
  when candidate_id is null 
    then 'INVALID'
    else 'VALID'
end as is_valid

from base 
qualify row_number() over(
    partition by candidate_id
    order by updated_at desc 
) = 1 
