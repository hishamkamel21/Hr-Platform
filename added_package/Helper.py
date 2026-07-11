import os

from dotenv import load_dotenv 
import pandas as pd 

load_dotenv()


class Helper:

    @staticmethod
    def get_watermark(target, schema):

        from .Engine import DatabaseManager 

        db = DatabaseManager()
        cursor = None

        try:
            cursor = db.get_snowflake_cursor(schema=schema)

            
            query = """
            SELECT max_timestamp, watermark_col
            FROM watermarks
            WHERE the_table = %s
            """
            
            cursor.execute(query, (target,))

            result = cursor.fetchone()

            if result is None:
                raise ValueError(
                    f"No watermark found for table '{target}'"
                 )

            timestamp, column = result

            return timestamp, column

        except Exception as e:
            raise Exception(f"Failed to get watermark: {e}")

        finally:
            if cursor is not None:
                cursor.close()
            db.close("snowflake")


    @staticmethod
    def get_max_timestamp(df, watermark_col):

        if df.empty:
            return None

        return df[watermark_col].max()
    
    @staticmethod
    def add_metadata_col(df):

        if df.empty:
            return None

        df["ingest_at"] = pd.Timestamp.utcnow()

        return df

    @staticmethod
    def update_watermark(target, value):

        from .Engine import DatabaseManager 

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

            cursor.execute(query, (formatted_value, target))

            cursor.connection.commit()

        except Exception as e:
            raise Exception(f"Failed to update watermark: {e}")

        finally:
            if cursor is not None:
                cursor.close()
            db.close("snowflake")


    @staticmethod
    def get_env(var=None, connection: str = None):

        if connection is not None:

            conn_dict = None

            if connection.lower().strip() == "postgres":

                database = os.getenv("SOURCE_DB")
                user = os.getenv("SOURCE_USER")
                password = os.getenv("SOURCE_PASSWORD")
                host = os.getenv("SOURCE_HOST")
                port = os.getenv("SOURCE_PORT")

                conn_dict = {
                    "database": database,
                    "user": user,
                    "password": password,
                    "host": host,
                    "port": port,
                }

                return conn_dict

            elif connection.lower().strip() == "snowflake":

                user = os.getenv("SNOWFLAKE_USER")
                password = os.getenv("SNOWFLAKE_PASSWORD")
                account = os.getenv("SNOWFLAKE_ACCOUNT")
                database = os.getenv("SNOWFLAKE_PROD_DB")
                warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
                schema = os.getenv("SNOWFLAKE_PROD_SCHEMA")

                conn_dict = {
                    "user": user,
                    "password": password,
                    "account": account,
                    "database": database,
                    "warehouse": warehouse,
                    "schema": schema,
                }

                return conn_dict

            else:
                raise ValueError("The connection is not correct.")

        elif var is not None:

            env_var = os.getenv(var)

            if env_var is None:
                raise ValueError(f"Environment variable '{var}' not found.")

            return env_var

        else:
            raise ValueError(
                "You should specify either 'connection' or 'var'."
            )