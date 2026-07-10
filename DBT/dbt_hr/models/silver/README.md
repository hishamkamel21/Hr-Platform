# models/silver/

Cleaned, standardized, incrementally-loaded staging models — one per bronze source entity. This is the first transformation layer on top of raw data.

## Models

| Model | Source table | Unique key | Notes |
|---|---|---|---|
| `departments.sql` | `bronze.departments` | `department_id` | Uppercases department name |
| `employees.sql` | `bronze.employees` | `employee_id` | Cleans name/email/phone, standardizes gender, parses date of birth |
| `jobs.sql` | `bronze.jobs` | `job_id` | Cleans job title/level, cleans salary range |
| `applications.sql` | `bronze.applications` | `application_id` | Parses application date/timestamp |
| `candidates.sql` | `bronze.candidates` | `candidate_id` | Builds `full_name` from first/last name |
| `interviews.sql` | `bronze.interviews` | `interview_id` | Validates `result` against accepted values, nulls score when pending |
| `offers.sql` | `bronze.offers` | `offer_id` | Cleans offered salary, parses offer/expiry/acceptance dates |
| `payrolls.sql` | `bronze.payrolls` | `payroll_id` | Cleans salary, bonus, deductions, tax, net salary |
| `posts.sql` | `bronze.posts` | `post_id` | Normalizes platform, parses posted/expiry timestamps |
| `sepations.sql` | `bronze.seprations` | `employee_id` | Separation type/reason, cleans last working day |

## Conventions

- **Materialization**: `incremental`, `unique_key` per table, `incremental_strategy = "merge"`, `on_schema_change = "append_new_columns"`.
- **Incremental filter**: pulls new/changed rows using `WHERE updated_at > (SELECT COALESCE(MAX(updated_at), '1900-01-01') FROM {{ this }})`.
- **Shared macros** (see [`/macros`](../../macros)):
  - `handle_ids(col)` — trims/uppercases and nullifies blank IDs.
  - `clean_salary(col)` — strips non-numeric characters and safely casts salary fields to a double.
  - `fix_date_format(col)` — parses multiple incoming date formats into a single `DATE`.
  - `accepted_values(col, accepted_values, alias)` — whitelists a column's values, defaulting invalid/blank values to `'N/A'`.
- Text fields are consistently `TRIM`/`UPPER` or `TRIM`/`LOWER`'d for consistent joins and grouping downstream.
- Rows that fail validation are **not** dropped here — they're captured separately in [`models/quartine`](../quartine).

