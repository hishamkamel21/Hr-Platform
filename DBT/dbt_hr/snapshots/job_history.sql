{% snapshot job_history %} 

{{
    config(
        target_schema = 'snapshots',
        unique_key = 'job_id',
        strategy = 'timestamp',
        updated_at = 'updated_at'
    )
}}

SELECT * 
FROM {{ref('jobs')}} 


{% endsnapshot %}