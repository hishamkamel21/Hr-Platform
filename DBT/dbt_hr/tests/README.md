# tests/

Custom singular data tests (in addition to any schema/generic tests defined in `.yml` files). A test "fails" if its query returns any rows.

## Subfolders

| Folder | Description |
|---|---|
| [`post_silver_tests/`](./post_silver_tests) | One test per entity, run after the `silver` layer builds, asserting required fields aren't null, keys are populated, and dates are sane. |

## Usage

```bash
dbt test                                  # run all tests
dbt test --select post_silver_tests       # run only silver-layer tests
dbt build                                 # run models + snapshots + tests together, respecting the DAG
```

A non-empty result set for any test file means that condition is currently being violated by data flowing through `silver` — worth cross-checking against [`models/quartine`](../models/quartine) to confirm those rows are being correctly quarantined rather than leaking into `gold`.
