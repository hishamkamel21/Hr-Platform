import logging
from snowflake.connector.pandas_tools import write_pandas
from .Engine import DatabaseManager

# Configure logger for this module
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


class Load:

    @staticmethod
    def to_snowflake(
        df,
        table_name: str,
        schema=None
    ) -> int:

        if df.empty:
            logger.warning(f"DataFrame provided for table '{table_name}' is empty. Skipping Snowflake write.")
            return 0

        row_count = len(df)
        logger.info(f"Initiating bulk write of {row_count} rows to Snowflake table '{table_name}'...")

        db = DatabaseManager()
        
        schema_upper = schema.upper() if schema else None
        conn = db.get_snowflake_connection(schema=schema_upper)

        df.columns = [col.upper() for col in df.columns]
        the_table = table_name.upper() 

        try:
            logger.debug(f"Executing write_pandas to table='{the_table}', schema='{schema_upper}'...")
            
            success, nchunks, nrows, _ = write_pandas(
                conn=conn,
                df=df,
                table_name=the_table,
                schema=schema_upper,            
                use_logical_type=True,          
                auto_create_table=False
            )

            if not success:
                err_msg = f"write_pandas reported failure when loading data into Snowflake table '{the_table}'"
                logger.error(err_msg)
                raise Exception(err_msg)

            logger.info(f"Successfully loaded {nrows} rows across {nchunks} chunk(s) into Snowflake table '{the_table}'.")
            return nrows

        except Exception as e:
            logger.exception(f"Failed to load data into Snowflake table '{the_table}': {e}")
            raise Exception(f"Failed to load data into {table_name}: {e}")

        finally:
            logger.debug("Closing Snowflake connection in Load.to_snowflake().")
            db.close("snowflake")