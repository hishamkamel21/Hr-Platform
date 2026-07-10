# models/quartine/

"Quarantine" models — one per entity — that isolate rows failing data quality or validation rules instead of silently dropping or letting them pollute the gold layer. Materialized as `table` (schema `quartine`) per `dbt_project.yml`.

## Models

| Model | Mirrors | What gets flagged/quarantined |
|---|---|---|
| `applications_q.sql` | `silver.applications` | Missing keys, invalid application dates |
| `candidates_q.sql` | `silver.candidates` | Invalid/incomplete candidate records |
| `departments_q.sql` | `silver.departments` | Bad department/manager references |
| `employees_q.sql` | `silver.employees` | Invalid employee attributes/dates |
| `interviews_q.sql` | `silver.interviews` | Bad interview stage/result/date combinations |
| `offers_q.sql` | `silver.offers` | Invalid offer status/salary/dates |
| `payrolls_q.sql` | `silver.payrolls` | Invalid payroll figures/dates |
| `posts_q.sql` | `silver.posts` | Invalid post/job/platform data |
| `seprations_q.sql` | `silver.seprations` | Null employee_id, invalid separation dates |

Note: `candidates_q.sql` is currently an empty file and needs its quarantine logic implemented, matching the pattern used in the other `*_q.sql` models.

## Pattern

Each model wraps the corresponding silver output in a `base` CTE, re-derives the same validation flags used in silver (e.g. via `foreign_key_check`), and selects only rows where `is_valid = 'INVALID'` (i.e. the complement of what flows into `gold`). This keeps quarantined records queryable for debugging upstream data issues without blocking the pipeline.

## Related

- [`models/silver`](../silver) — the models these quarantine tables validate against.
- [`macros/foreign_key_check.sql`](../../macros/foreign_key_check.sql) — used to flag broken foreign key relationships.
- [`tests/post_silver_tests`](../../tests/post_silver_tests) — automated tests that assert invalid rows don't leak into the valid/gold path.
