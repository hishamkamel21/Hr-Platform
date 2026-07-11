
with grouped as ( 
    select 
    department_id ,
    count(*) as Total_Employees ,

    count(
        case 
          when employee_status = 'ACTIVE' then 1 end 
    ) as Total_Active_Employees ,

    count(
        case 
          when employee_status = 'TERMINATED' then 1 end 
    ) as Total_Terminated_Employees ,

    round(avg(age),2) as Avg_Employees_Age 
    
    from {{ref('employees')}} 
    where is_valid = 'VALID'
    group by department_id 
)
select * 
from grouped 

 