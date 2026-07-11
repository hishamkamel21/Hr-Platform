# models/intermidate/

Reusable intermediate transformations that sit between `silver` and `gold`/`snapshots`. Materialized as `view` (schema `silver`) per `dbt_project.yml`.

## Models

| Model | Description |
|---|---|
| `current_salary.sql` | For each `employee_id`, picks the most recent payroll record (`qualify row_number() ... = 1` ordered by `payment_date desc`) to get each employee's current monthly salary. Sources from valid rows in `silver.payrolls`. |
| `total_employees.sql` | Aggregates `silver.employees` by `department_id` into `Total_Employees`, `Total_Active_Employees`, `Total_Terminated_Employees`, and `Avg_Employees_Age`. Feeds the department snapshot (`snapshots/department_history.sql` reads from a model built on top of this, e.g. `latest_department_update`). |

## Purpose

These models exist so that headcount/salary logic used by snapshots (SCD2 history) and gold facts doesn't need to be duplicated across multiple downstream models — compute once here, `ref()` it everywhere else.
