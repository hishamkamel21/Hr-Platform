with stat as ( 
    select 
    department_id ,
    Total_employees , 
    Total_Active_Employees ,
    Total_Terminated_Employees ,
    Avg_Employees_Age

    from {{ref("department_history")}} 
    where dbt_valid_to is null 
)
select * 
from stat