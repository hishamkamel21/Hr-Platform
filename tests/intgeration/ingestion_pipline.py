"""
Module: test_ingestion_pipeline.py
Description:
    Integration test runner for verifying the PostgreSQL -> Snowflake ETL pipeline.
    Queries the metadata catalog for watermark state, extracts batch data, enriches records with metadata,
    loads rows to Snowflake, validates row count assertions, and updates the watermark on success.
"""

import sys
from datetime import datetime
from added_package.Helper import Helper 
from added_package.Extract import Extract 
from added_package.Load import Load


def test_ingestion_pipline():
    """
    Executes end-to-end integration test for target table 'ids'.
    
    Raises:
        ValueError: If row count loaded to Snowflake fails assertion check.
        Exception: Captures and handles underlying database, extract, or load failures.
    """
    print("Starting ingestion pipeline integration test...")

    try:
        # Step 1: Fetch current watermark timestamp and column name from metadata catalog
        print("Fetching watermark metadata for target 'ids'...")
        the_timestamp, watermark_col = Helper.get_watermark(
            target="ids",
            schema="metadata"
        )
        print(f"Retrieved watermark column '{watermark_col}' with boundary: {the_timestamp}")

        # Step 2: Extract incremental dataset from source PostgreSQL database
        print("Extracting data from PostgreSQL source schema 'test'...")
        df = Extract.from_postgres(
            table="ids",
            schema="test",
            max_timestamp=the_timestamp,
            watermark_column=watermark_col
        )

        # Early guardrail: Check if extracted DataFrame contains rows
        if df is None or df.empty:
            print("Extracted DataFrame is empty. Skipping processing.")
            return

        print(f"Successfully extracted {len(df)} rows from PostgreSQL.")

        # Step 3: Compute upper timestamp boundary from extracted batch
        new_max_timestamp = Helper.get_max_timestamp(df=df, watermark_col=watermark_col)

        # Step 4: Add audit metadata columns to DataFrame
        print("Adding ETL metadata auditing columns...")
        last_df = Helper.add_metadata_col(df=df)

        # Step 5: Write dataset into Snowflake destination table and retrieve loaded row count
        print("Loading processed records into Snowflake target 'TEST.IDS'...")
        rows = Load.to_snowflake(
            df=last_df,
            table_name="IDS",
            schema="TEST"
        )
        print(f"Snowflake load completed. Total rows inserted: {rows}")

        # Step 6: Validate output against target row count assertion
        EXPECTED_ROWS = 10
        if rows != EXPECTED_ROWS:
            raise ValueError(
                f"The ingestion test failed! Expected {EXPECTED_ROWS} rows, but got {rows}."
            )

        # Step 7: Update watermark state in catalog upon successful validation
        print("Validation passed. Updating watermark state in metadata catalog...")
        Helper.update_watermark(
            target="ids",
            value=new_max_timestamp
        )

        print("The test succeeded.")

    # Exception Handler 1: Catch specific row count assertion failures
    except ValueError as val_err:
        print(f"[ERROR] Data Validation Failed: {val_err}")
        raise

    # Exception Handler 2: Catch general execution errors (database connections, bad credentials)
    except Exception as err:
        print(f"[CRITICAL] Pipeline execution failed due to an error: {err}")
        sys.exit(1)


if __name__ == '__main__':
    # Entry point for standalone execution
    test_ingestion_pipline()