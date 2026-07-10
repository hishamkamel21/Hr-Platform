{{
    config(
        materialized="incremental",
        unique_key="employee_id",
        incremental_strategy="merge",
        on_schema_change = "append_new_columns"
    )
}}
WITH base AS (

    SELECT
        {{ handle_Ids('employee_id') }} AS employee_id,
        LOWER(TRIM(first_name)) AS first_name,
        LOWER(TRIM(last_name)) AS last_name,

        COALESCE(email, 'N/A') AS email,
        COALESCE(phone, 'N/A') AS phone,

        CASE
            WHEN LOWER(gender) LIKE 'm%' THEN 'M'
            WHEN LOWER(gender) LIKE 'f%' THEN 'F'
            ELSE 'O'
        END AS gender,

        {{ fix_date_formats('date_of_birth') }} AS date_of_birth,
        {{ fix_date_formats('hire_date') }} AS hire_date,

        CASE
            WHEN termination_date IS NOT NULL
                THEN {{ fix_date_formats('termination_date') }}
            ELSE NULL
        END AS termination_date,

        {{ handle_Ids('manager_id') }} AS manager_id,
        {{ handle_Ids('department_id') }} AS department_id,
        {{ handle_Ids('job_id') }} AS job_id,

        {{
            accepted_values(
                col='status',
                accepted_values="('ACTIVE','TERMINATED')",
                alias='employee_status'
            )
        }},

        {{
            accepted_values(
                col='education_level',
                accepted_values="('BACHELOR','HIGH SCHOOL','MASTER','PHD')",
                alias='education_level'
            )
        }},

        created_at,
        updated_at,
        ingest_at

    FROM {{ source('bronze', 'employees') }}

    {% if is_incremental() %}
        WHERE updated_at >
        (
            SELECT COALESCE(MAX(updated_at), '1900-01-01')
            FROM {{ this }}
        )
    {% endif %}

),
stage AS (

    SELECT
        e.*,
        DATEDIFF(year, date_of_birth, CURRENT_DATE()) AS age,

        CONCAT(first_name, ' ', last_name) AS full_name
    FROM base e
    QUALIFY ROW_NUMBER() OVER
    (
        PARTITION BY employee_id
        ORDER BY updated_at DESC
    ) = 1

),
add_salary AS (

    SELECT
        e.*,
        s.month_salary
    FROM stage e
    LEFT JOIN {{ ref('current_salary') }} s
        ON e.employee_id = s.employee_id
)
SELECT
    employee_id,
    full_name,
    email,
    phone,
    gender,
    age,
    date_of_birth,
    hire_date,
    termination_date,
    manager_id,
    department_id,
    job_id,
    employee_status,
    education_level,
    month_salary,
    created_at,
    updated_at,
    ingest_at,
    CASE
        WHEN employee_id IS NULL THEN 'INVALID'
        WHEN job_id IS NULL THEN 'INVALID'
        WHEN department_id IS NULL THEN 'INVALID'
        WHEN hire_date > CURRENT_DATE() THEN 'INVALID'
        WHEN termination_date > CURRENT_DATE() THEN 'INVALID'
        ELSE 'VALID'
    END AS is_valid

FROM add_salary