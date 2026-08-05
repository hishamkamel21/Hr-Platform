import logging
import os

from dotenv import load_dotenv 
import pandas as pd 

# Configure logger for this module
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

load_dotenv()


class Helper:

    @staticmethod
    def get_watermark(target, schema):
        from .Engine import DatabaseManager 

        logger.info(f"Fetching watermark for table '{target}' in schema '{schema}'...")
        db = DatabaseManager()
        cursor = None

        try:
            cursor = db.get_snowflake_cursor(schema=schema)
            
            query = """
            SELECT max_timestamp, watermark_col
            FROM watermarks
            WHERE the_table = %s
            """
            
            logger.debug(f"Executing query to retrieve watermark for '{target}'")
            cursor.execute(query, (target,))
            result = cursor.fetchone()

            if result is None:
                err_msg = f"No watermark found for table '{target}'"
                logger.error(err_msg)
                raise ValueError(err_msg)

            timestamp, column = result
            logger.info(f"Successfully retrieved watermark for '{target}': column='{column}', timestamp='{timestamp}'")
            return timestamp, column

        except Exception as e:
            logger.exception(f"Failed to get watermark for table '{target}': {e}")
            raise Exception(f"Failed to get watermark: {e}")

        finally:
            if cursor is not None:
                logger.debug("Closing Snowflake cursor for get_watermark.")
                cursor.close()
            db.close("snowflake")

    @staticmethod
    def get_max_timestamp(df, watermark_col):
        if df.empty:
            logger.warning(f"DataFrame is empty. Cannot compute max timestamp for column '{watermark_col}'. Returning None.")
            return None

        if watermark_col not in df.columns:
            err_msg = f"Watermark column '{watermark_col}' not found in DataFrame columns."
            logger.error(err_msg)
            raise KeyError(err_msg)

        max_val = df[watermark_col].max()
        logger.info(f"Computed max timestamp for '{watermark_col}': {max_val}")
        return max_val
    
    @staticmethod
    def add_metadata_col(df):
        if df.empty:
            logger.warning("DataFrame is empty. Skipping addition of 'ingest_at' metadata column.")
            return None

        df["ingest_at"] = pd.Timestamp.utcnow()
        logger.info(f"Added 'ingest_at' metadata column across {len(df)} rows.")
        return df

    @staticmethod
    def update_watermark(target, value):
        from .Engine import DatabaseManager 

        logger.info(f"Updating watermark for table '{target}' to new value: '{value}'...")
        db = DatabaseManager()
        cursor = None

        try:
            cursor = db.get_snowflake_cursor(schema="metadata")
            
            query = """
            UPDATE watermarks
            SET Max_Timestamp = %s
            WHERE the_table = %s
            """
        
            if hasattr(value, 'strftime'):
                formatted_value = value.strftime('%Y-%m-%d %H:%M:%S.%f')
            else:
                formatted_value = str(value)

            logger.debug(f"Executing update for table '{target}' with timestamp parameter '{formatted_value}'")
            cursor.execute(query, (formatted_value, target))
            cursor.connection.commit()

            logger.info(f"Successfully updated and committed watermark for table '{target}'.")

        except Exception as e:
            logger.exception(f"Failed to update watermark for table '{target}': {e}")
            raise Exception(f"Failed to update watermark: {e}")

        finally:
            if cursor is not None:
                logger.debug("Closing Snowflake cursor for update_watermark.")
                cursor.close()
            db.close("snowflake")

    @staticmethod
    def get_env(var=None, connection: str = None):
        if connection is not None:
            conn_type = connection.lower().strip()
            logger.info(f"Fetching environment configuration for connection type: '{conn_type}'")

            if conn_type == "postgres":
                conn_dict = {
                    "database": os.getenv("SOURCE_DB"),
                    "user": os.getenv("SOURCE_USER"),
                    "password": os.getenv("SOURCE_PASSWORD"),
                    "host": os.getenv("SOURCE_HOST"),
                    "port": os.getenv("SOURCE_PORT"),
                }
                
                # Check for missing values to warn early
                missing_keys = [k for k, v in conn_dict.items() if v is None]
                if missing_keys:
                    logger.warning(f"PostgreSQL connection config missing variables: {missing_keys}")

                return conn_dict

            elif conn_type == "snowflake":
                conn_dict = {
                    "user": os.getenv("SNOWFLAKE_USER"),
                    "password": os.getenv("SNOWFLAKE_PASSWORD"),
                    "account": os.getenv("SNOWFLAKE_ACCOUNT"),
                    "database": os.getenv("SNOWFLAKE_PROD_DB"),
                    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
                    "schema": os.getenv("SNOWFLAKE_PROD_SCHEMA"),
                }

                missing_keys = [k for k, v in conn_dict.items() if v is None]
                if missing_keys:
                    logger.warning(f"Snowflake connection config missing variables: {missing_keys}")

                return conn_dict

            else:
                err_msg = f"Unsupported connection type '{connection}'. Expected 'postgres' or 'snowflake'."
                logger.error(err_msg)
                raise ValueError(err_msg)

        elif var is not None:
            logger.debug(f"Fetching environment variable '{var}'")
            env_var = os.getenv(var)

            if env_var is None:
                err_msg = f"Environment variable '{var}' not found."
                logger.error(err_msg)
                raise ValueError(err_msg)

            return env_var

        else:
            err_msg = "Must specify either 'connection' or 'var' parameter in get_env()."
            logger.error(err_msg)
            raise ValueError(err_msg)