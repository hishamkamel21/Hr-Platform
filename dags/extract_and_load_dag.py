"""
DAG Title: Extract_And_Load
Description:
    Orchestrates incremental extraction of HR-related tables from PostgreSQL,
    enriches extracted DataFrames with metadata tracking columns, updates Snowflake
    data warehouse target tables, and persists state via watermarks in the metadata layer.
"""

from datetime import datetime

from added_package.Helper import Helper
from added_package.Extract import Extract
from added_package.Load import Load
from airflow.sdk import dag, task


def extract_and_load(watermark_dict: dict, table: str) -> None:
    """
    Core ETL pipeline helper function for a single database table.

    Steps:
    1. Parses watermark column and last processed timestamp.
    2. Extracts incremental records from PostgreSQL database where timestamp > watermark_ts.
    3. Exits early if no new rows are extracted.
    4. Computes updated max timestamp from extracted batch.
    5. Injects ETL auditing metadata columns (e.g., ingest timestamps).
    6. Loads enriched DataFrame into Snowflake target table.
    7. Updates the watermark timestamp in the metadata catalog for future runs.

    Args:
        watermark_dict (dict): Dictionary containing 'watermark_column' and 'watermark_timestamp'.
        table (str): Target table name being processed.
    """
    watermark_col = watermark_dict['watermark_column']
    watermark_ts = watermark_dict['watermark_timestamp']

    # Convert ISO string representation back to datetime object if passed across Airflow XComs
    if isinstance(watermark_ts, str):
        watermark_ts = datetime.fromisoformat(watermark_ts)

    # Step 1: Extract delta dataset from source PostgreSQL table using watermark boundary
    df = Extract.from_postgres(
        table=table,
        watermark_column=watermark_col,
        max_timestamp=watermark_ts,
        schema="hr"
    )

    # Early exit guardrail: terminate execution if no new rows were updated/created
    if df.empty:
        print(f"The dataframe for {table} is empty. Skipping execution.")
        return

    # Step 2: Compute new max timestamp from current batch to advance watermark boundary
    new_max = Helper.get_max_timestamp(df=df)

    # Step 3: Append administrative and ETL audit columns to DataFrame
    last_df = Helper.add_metadata_col(df=df)

    # Step 4: Write enriched dataset into Snowflake destination table
    Load.to_snowflake(df=last_df, table_name=table)

    # Step 5: Persist updated watermark state in metadata database
    Helper.update_watermark(target=table, value=new_max)


@dag(dag_id="Extract_And_Load", schedule=None)
def Extract_And_Load():
    """
    Airflow DAG definition using TaskFlow API. Handles multi-table database extraction
    and ingestion routines with resource concurrency management via connection pools.
    """

    @task
    def get_tables_task() -> list:
        """
        Retrieves list of target schema tables scheduled for incremental processing.

        Returns:
            list: List of table strings to be processed.
        """
        return [
            "jobs", "departments", "offers", "applications", 
            "employees", "seprations", "candidates", "payrolls", 
            "posts", "interviews"
        ]

    @task
    def set_watermarks_task(tables_list: list) -> dict:
        """
        Fetches current state metadata (watermark timestamps and column names) 
        for all target tables from the central metadata store.

        Args:
            tables_list (list): Array of table names to query metadata for.

        Returns:
            dict: Dictionary containing ISO-formatted watermark configurations mapped per table.
        """
        watermark_dict = {}

        for table in tables_list:
            # Query watermark catalog table for target schema table metadata
            watermark_time, watermark_col = Helper.get_watermark(target=table, schema="metadata")

            watermark_dict[table] = {
                "watermark_column": watermark_col,
                "watermark_timestamp": watermark_time.isoformat() if watermark_time else None
            }

        return watermark_dict

    @task(pool="connection_pool")
    def extract_and_load_table(watermarks: dict, table: str) -> None:
        """
        Executes incremental extraction and load process for an individual table.
        Uses Airflow pool `connection_pool` to restrict concurrent connection usage.

        Args:
            watermarks (dict): Full dictionary mapping all table watermarks.
            table (str): Specific table name being processed.
        """
        table_dict = watermarks[table]

        # Invoke core ETL process function
        extract_and_load(table_dict, table)

    # Step 1: Initialize list of tables to process
    tables = get_tables_task()

    # Step 2: Retrieve state watermarks from catalog before processing batch
    all_watermarks = set_watermarks_task(tables)

    # Step 3: Instantiate individual extraction tasks per target table
    # Note: These tasks pass `all_watermarks` via XCom and run as independent DAG nodes
    extract_and_load_table(all_watermarks, 'employees')
    extract_and_load_table(all_watermarks, 'departments')
    extract_and_load_table(all_watermarks, 'offers')
    extract_and_load_table(all_watermarks, 'jobs')
    extract_and_load_table(all_watermarks, 'applications')
    extract_and_load_table(all_watermarks, 'interviews')
    extract_and_load_table(all_watermarks, 'seprations')
    extract_and_load_table(all_watermarks, 'posts')
    extract_and_load_table(all_watermarks, 'candidates')
    extract_and_load_table(all_watermarks, 'payrolls')


# Instantiate the DAG object
Extract_And_Load()