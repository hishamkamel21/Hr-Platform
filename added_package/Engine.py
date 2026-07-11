import psycopg2
import snowflake.connector

from .Helper import Helper


class DatabaseManager:

    def __init__(self):
        self.postgres_conn = None
        self.snowflake_conn = None

    def get_postgres_connection(self):

        if self.postgres_conn is None or self.postgres_conn.closed: 

            config = Helper.get_env(connection="postgres")

            self.postgres_conn = psycopg2.connect(
                dbname=config["database"],
                user=config["user"],
                password=config["password"],
                host=config["host"],
                port=config["port"],
                sslmode="require"
            )

        return self.postgres_conn

    def get_snowflake_connection(self, schema=None):

        if (
            self.snowflake_conn is None
            or self.snowflake_conn.is_closed()
        ):

            config = Helper.get_env(connection="snowflake")

            self.snowflake_conn = snowflake.connector.connect(
                user=config["user"],
                password=config["password"],
                account=config["account"],
                warehouse=config["warehouse"],
                database=config["database"],
                schema=schema or config["schema"],
            )

        return self.snowflake_conn

    def get_postgres_cursor(self):

        return self.get_postgres_connection().cursor()

    def get_snowflake_cursor(self, schema=None):

        return self.get_snowflake_connection(schema).cursor()

    def close(self, connection):

        if connection.lower() == "postgres":

            if self.postgres_conn is not None:
                try:
                    self.postgres_conn.close()
                finally:
                    self.postgres_conn = None

        elif connection.lower() == "snowflake":

            if self.snowflake_conn is not None:
                try:
                    self.snowflake_conn.close()
                finally:
                    self.snowflake_conn = None

        else:
            raise ValueError(
                "connection must be 'postgres' or 'snowflake'"
            )