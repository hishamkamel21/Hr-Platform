{% snapshot department_history %} 

{{ config(
    target_schema = 'snapshot',
    unique_key = 'department_id',
    strategy = 'check',
    check_cols = [ 
        'manager_id',
        'Total_Employees',
        'Total_Active_Employees',
        'Total_Terminated_Employees',
        'Avg_Employees_Age'
    ]
) }}

SELECT * 
FROM {{ref('departments')}} 
where is_valid = 'VALID'

{% endsnapshot %} 
