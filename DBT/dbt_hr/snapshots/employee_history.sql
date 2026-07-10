{% snapshot employee_history %} 

{{
    config(
        target_schema = 'snapshot',
        unique_key = 'employee_id',
        strategy = 'timestamp',
        updated_at = 'updated_at'
    )
}}

SELECT * 
FROM {{ref('employees')}}  
where is_valid = 'VALID'
{% endsnapshot %} 
