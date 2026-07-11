# snapshots/

dbt snapshots that implement **SCD Type 2** history for slowly-changing HR entities, run via `dbt snapshot` and stored in the `snapshot`/`snapshots` schema.

## Snapshots

| File | Snapshot name | Strategy | Unique key | Tracks changes in |
|---|---|---|---|---|
| `department_history.sql` | `department_history` | `check` (`check_cols`) | `department_id` | `manager_id`, `Total_Employees`, `Total_Active_Employees`, `Total_Terminated_Employees`, `Avg_Employees_Age` |
| `employee_history.sql` | `employee_history` | `timestamp` (`updated_at`) | `employee_id` | Any employee attribute, whenever `updated_at` changes |
| `jobs_history.sql` | `jobs_history` | `timestamp` (`updated_at`) | `job_id` | Any job attribute, whenever `updated_at` changes |

Each snapshot reads from an intermediate "latest state" model (e.g. `latest_department_update`, `latest_employee_update`, `latest_job_update`) and dbt appends `dbt_valid_from`/`dbt_valid_to` columns to track when each version of a row was current.

## How the gold layer uses these

`models/gold/dim_departments.sql`, `dim_employees.sql`, and `dim_jobs.sql` all read from these snapshots and filter `WHERE dbt_valid_to IS NULL` to expose only the current version of each record as a dimension table.

## ⚠️ Important — snapshot naming

Every `{% snapshot %}` block **must** have a name immediately after `snapshot`, and that name must match what downstream models `ref()`:

```sql
{% snapshot department_history %}   -- ✅ correct

{% snapshot %}                      -- ❌ causes:
                                     --   Parsing Error
                                     --   at path ['name']: None is not of type 'string'
```

`department_history.sql` previously had a missing name — make sure it stays as `{% snapshot department_history %}` after any future edits, and that `models/gold/dim_employees.sql` / `dim_jobs.sql` reference the exact snapshot names `employee_history` / `jobs_history` (not `employees_history`).

## Usage

```bash
dbt snapshot                       # run all snapshots
dbt snapshot --select department_history
```
