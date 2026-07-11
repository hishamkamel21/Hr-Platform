from datetime import datetime

from added_package.Helper import Helper
from added_package.Extract import Extract
from added_package.Load import Load
from airflow.sdk import dag, task


def extract_and_load(watermark_dict, table):

    watermark_col = watermark_dict['watermark_column']
    watermark_ts = watermark_dict['watermark_timestamp']

    if isinstance(watermark_ts, str):
        watermark_ts = datetime.fromisoformat(watermark_ts)

    df = Extract.from_postgres(
        table=table,
        watermark_column=watermark_col,
        max_timestamp=watermark_ts,
        schema="hr"
    )

    if df.empty:
        print(f"The dataframe for {table} is empty. Skipping execution.")
        return

    new_max = Helper.get_max_timestamp(df=df)

    last_df = Helper.add_metadata_col(df=df)

    Load.to_snowflake(df=last_df, table_name=table)

    Helper.update_watermark(target=table, value=new_max)


@dag(dag_id="Extract_And_Load", schedule=None)
def Extract_And_Load():

    @task
    def get_tables_task():
        return ["jobs", "departments", "offers", "applications", "employees", "seprations", "candidates", "payrolls", "posts", "interviews"]

    @task
    def set_watermarks_task(tables_list):
        watermark_dict = {}

        for table in tables_list:

            watermark_time, watermark_col = Helper.get_watermark(target=table, schema="metadata")

            watermark_dict[table] = {
                "watermark_column": watermark_col,
                "watermark_timestamp": watermark_time.isoformat() if watermark_time else None
            }

        return watermark_dict

    @task(pool="connection_pool")
    def extract_and_load_table(watermarks: dict, table: str):

        table_dict = watermarks[table]

        extract_and_load(table_dict, table)

    tables = get_tables_task()

    all_watermarks = set_watermarks_task(tables)

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


Extract_And_Load()
