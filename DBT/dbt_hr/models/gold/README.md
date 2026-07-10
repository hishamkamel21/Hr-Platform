# models/gold/

The final dimensional model of the warehouse — dimension (`dim_*`) and fact (`fact_*`) tables ready for BI/reporting tools. Materialized `incremental` (schema `gold`) per `dbt_project.yml`, with a couple of `view`-style SCD2 pass-throughs.

## Dimensions

| Model | Source | Notes |
|---|---|---|
| `dim_applications.sql` | `ref('applications')` | Valid applications only, incremental merge on `application_id` |
| `dim_candidates.sql` | `ref('candidates')` | Valid candidates only, incremental merge on `candidate_id` |
| `dim_departments.sql` | `ref('department_history')` | Reads the snapshot, filters `dbt_valid_to IS NULL` + `is_current = True` for the current state (SCD2 "current" view) |
| `dim_employees.sql` | `ref('employees_history')` | Same SCD2 pattern as departments |
| `dim_jobs.sql` | `ref('jobs_history')` | Same SCD2 pattern as departments |
| `dim_posts.sql` | `ref('posts')` | Valid posts only, incremental merge on `post_id` |

## Facts

| Model | Source | Notes |
|---|---|---|
| `fact_offers.sql` | `ref('offers')` | Adds `is_hired` flag based on `acceptance_date` |
| `fact_hiring.sql` | `ref('fact_offers')` | Filters to `is_hired = 1`, tracks accepted salary/date |
| `fact_interviews.sql` | `ref('interviews')` | Valid interviews only, incremental merge on `interview_id` |
| `fact_payrolls.sql` | `ref('payrolls')` | Valid payroll rows only, incremental merge on `payroll_id` |
| `fact_turnover.sql` | `ref('seprations')` | Employee separations feeding turnover analysis |

