import logging
import pandas as pd

from .Engine import DatabaseManager
from .Helper import Helper 

# Configure logger for this module
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


class Extract:

    @staticmethod
    def from_postgres(
        table: str,
        watermark_column: str,
        max_timestamp,
        schema
    ) -> pd.DataFrame:

        logger.info(f"Initiating extraction from Postgres for table '{schema}.{table}'...")
        logger.debug(f"Parameters: watermark_column='{watermark_column}', max_timestamp='{max_timestamp}'")

        db = DatabaseManager()
        
        try:
            conn = db.get_postgres_connection()
            logger.debug("Successfully established PostgreSQL connection.")

            query = f"""
                SELECT *
                FROM {schema}.{table}
                WHERE {watermark_column} > %s
            """

            logger.info(f"Executing extraction query on '{schema}.{table}'...")
            df = pd.read_sql_query(
                sql=query,
                con=conn,
                params=[max_timestamp]
            ) 

            row_count = len(df)
            logger.info(f"Extracted {row_count} rows from '{schema}.{table}'.")

            if row_count == 0:
                logger.warning(f"No new records found in '{schema}.{table}' past timestamp '{max_timestamp}'.")

            logger.debug("Appending metadata columns to DataFrame...")
            df = Helper.add_metadata_col(df) 
            
            return df

        except Exception as e:
            logger.exception(f"Failed to extract data from PostgreSQL for table '{schema}.{table}': {e}")
            raise Exception(f"PostgreSQL extraction failed: {e}")

        finally:
            logger.debug("Closing PostgreSQL database connection.")
            db.close("postgres")