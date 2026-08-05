import logging
import psycopg2
import snowflake.connector

from .Helper import Helper

# Configure logger for this module
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


class DatabaseManager:

    def __init__(self):
        self.postgres_conn = None
        self.snowflake_conn = None

    def get_postgres_connection(self):
        if self.postgres_conn is None or self.postgres_conn.closed:
            logger.info("Initializing new PostgreSQL connection...")
            
            try:
                config = Helper.get_env(connection="postgres")
                
                self.postgres_conn = psycopg2.connect(
                    dbname=config["database"],
                    user=config["user"],
                    password=config["password"],
                    host=config["host"],
                    port=config["port"],
                    sslmode="require"
                )
                logger.info("PostgreSQL connection established successfully.")
            except Exception as e:
                logger.exception(f"Failed to connect to PostgreSQL: {e}")
                raise Exception(f"PostgreSQL connection error: {e}")
        else:
            logger.debug("Reusing existing PostgreSQL connection.")

        return self.postgres_conn

    def get_snowflake_connection(self, schema=None):
        if (
            self.snowflake_conn is None
            or self.snowflake_conn.is_closed()
        ):
            target_schema = schema or "default"
            logger.info(f"Initializing new Snowflake connection (schema='{target_schema}')...")
            
            try:
                config = Helper.get_env(connection="snowflake")

                self.snowflake_conn = snowflake.connector.connect(
                    user=config["user"],
                    password=config["password"],
                    account=config["account"],
                    warehouse=config["warehouse"],
                    database=config["database"],
                    schema=schema or config["schema"],
                )
                logger.info("Snowflake connection established successfully.")
            except Exception as e:
                logger.exception(f"Failed to connect to Snowflake: {e}")
                raise Exception(f"Snowflake connection error: {e}")
        else:
            logger.debug("Reusing existing Snowflake connection.")

        return self.snowflake_conn

    def get_postgres_cursor(self):
        logger.debug("Creating new PostgreSQL cursor.")
        return self.get_postgres_connection().cursor()

    def get_snowflake_cursor(self, schema=None):
        logger.debug(f"Creating new Snowflake cursor for schema '{schema}'.")
        return self.get_snowflake_connection(schema).cursor()

    def close(self, connection):
        conn_type = connection.lower().strip()

        if conn_type == "postgres":
            if self.postgres_conn is not None:
                logger.info("Closing PostgreSQL connection...")
                try:
                    self.postgres_conn.close()
                    logger.info("PostgreSQL connection closed successfully.")
                except Exception as e:
                    logger.error(f"Error while closing PostgreSQL connection: {e}")
                finally:
                    self.postgres_conn = None
            else:
                logger.debug("PostgreSQL connection already closed or uninitialized.")

        elif conn_type == "snowflake":
            if self.snowflake_conn is not None:
                logger.info("Closing Snowflake connection...")
                try:
                    self.snowflake_conn.close()
                    logger.info("Snowflake connection closed successfully.")
                except Exception as e:
                    logger.error(f"Error while closing Snowflake connection: {e}")
                finally:
                    self.snowflake_conn = None
            else:
                logger.debug("Snowflake connection already closed or uninitialized.")

        else:
            err_msg = f"Invalid connection type '{connection}'. Must be 'postgres' or 'snowflake'."
            logger.error(err_msg)
            raise ValueError(err_msg)