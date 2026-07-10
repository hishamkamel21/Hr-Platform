import pandas as pd

from .Engine import DatabaseManager
from .Helper import Helper 

class Extract:

    @staticmethod
    def from_postgres(
        table: str,
        watermark_column: str,
        max_timestamp,
        schema
    ) -> pd.DataFrame:

        db = DatabaseManager()
        conn = db.get_postgres_connection()

        try:
            query = f"""
                SELECT *
                FROM {schema}.{table}
                WHERE {watermark_column} > %s
            """

            df = pd.read_sql_query(
                sql=query,
                con=conn,
                params=[max_timestamp]
            ) 

            df = Helper.add_metadata_col(df) 
            
            return df

        finally:
            db.close("postgres")