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
    {{ handle_Ids('interview_id') }} as interview_id,
    {{ handle_Ids('application_id')}} as application_id,
    {{ handle_Ids('interviewer_id')}} as interviewer_id,
    upper(trim(interview_stage)) as interview_stage ,
    to_timestamp(interview_date) as interview_timestamp,
    to_date(interview_date) as interview_date ,
    case 
      when upper(trim(result)) = 'PENDING' 
       then null 
      else try_cast(score as double)
    end as score  ,
    {{ accepted_values(
        col = 'result',
        accepted_values="('PASS','FAIL','PENDING')",
        alias = 'result'
    )}},
    created_at ,
    updated_at,
    ingest_at 

    from {{ source('bronze','interviews')}} 
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
    * , 
    {{ foreign_key_check(
        main = 'iv',
        ref_model = 'applications',
        foreign_key = 'application_id',
        add_ref_validity = TRUE ,
        alias = 'foreign_application_error'
    ) }} ,

    {{ foreign_key_check(
        main = 'iv' ,
        ref_model = 'employees', 
        foreign_key = 'interviewer_id',
        add_ref_validity = TRUE ,
        ref_foreign_key = 'employee_id',
        alias = 'foreign_employee_error'
    ) }} 

    from base iv
    qualify row_number() over(
        partition by iv.interview_id 
        order by iv.updated_at desc 
    ) = 1 
),
final as ( 
    select 
    interview_id ,
    application_id ,
    interviewer_id ,
    interview_stage ,
    interview_date ,
    interview_timestamp,
    score , 
    result ,
    created_at ,
    updated_at,
    ingest_at ,
    foreign_application_error,
    foreign_employee_error,

    CASE 
      WHEN interview_id is null or 
       application_id is null or 
       interviewer_id is null or 
       interview_date is null or 
       interview_timestamp is null or   
       result is null or 
       foreign_application_error = 1 or 
       foreign_employee_error = 1 or 
       interview_date > current_date()
      THEN 'INVALID' 
      ELSE 'VALID' 
    END AS is_valid

    from stage 
)
SELECT * 
FROM final  
