# macros/

Reusable Jinja/SQL macros used across the `silver` and `quartine` layers for cleaning, standardizing, and validating raw HR/ATS data.

## Macros

| Macro | File | Signature | Purpose |
|---|---|---|---|
| `handle_ids` | `handle_ids.sql` | `handle_ids(col)` | Trims and uppercases an ID column; returns `NULL` if blank/null, so downstream joins are safe and consistent. |
| `clean_salary` | `clean_salary.sql` | `clean_salary(col)` | Strips leading non-numeric characters from a salary field and safely `TRY_CAST`s it to a numeric type; returns `NULL` if it can't be parsed. |
| `fix_date_format` | `fix_date_formats.sql` | `fix_date_format(col)` | Tries multiple common date formats (`YYYY-MM-DD`, `DD-MM-YYYY`, `MM/DD/YYYY`, etc.) via `COALESCE(TRY_TO_DATE(...), ...)` and returns the first that parses. |
| `accepted_values` | `accecpted_values.sql` | `accepted_values(col, accepted_values, alias)` | Whitelists a column against a fixed set of accepted values; blank/null/unlisted values become `'N/A'`. |
| `foreign_key_check` | `foreign_key_check.sql` | `foreign_key_check(main, ref_model, foreign_key, alias, add_ref_validity=false, ref_foreign_key=None, diff_key=false)` | Returns `1`/`0` flagging whether a row's foreign key exists in a referenced model (optionally requiring the referenced row to also be `is_valid = 'VALID'`), used to build validity/quarantine logic. |

## Usage example

```sql
select
    {{ handle_ids('employee_id') }} as employee_id,
    {{ clean_salary('salary') }} as salary,
    {{ fix_date_format('hire_date') }} as hire_date,
    {{ accepted_values(
        col = 'status',
        accepted_values = "('ACTIVE','TERMINATED')",
        alias = 'status'
    ) }},
    {{ foreign_key_check(
        main = 'e',
        ref_model = 'departments',
        foreign_key = 'department_id',
        alias = 'department_fk_valid'
    ) }}
from {{ source('bronze', 'employees') }} e
```

