from snowflake.connector.pandas_tools import write_pandas
from .Engine import DatabaseManager

class Load:

    @staticmethod
    def to_snowflake(
        df,
        table_name: str,
        schema=None
    ) -> int:

        if df.empty:
            return 0

        db = DatabaseManager()
        
        schema_upper = schema.upper() if schema else None
        
        conn = db.get_snowflake_connection(schema=schema_upper)

       
        df.columns = [col.upper() for col in df.columns]
        the_table = table_name.upper() 

        try:
            success, nchunks, nrows, _ = write_pandas(
                conn=conn,
                df=df,
                table_name=the_table,
                schema=schema_upper,            
                use_logical_type=True,          
                auto_create_table=False
            )

            if not success:
                raise Exception(
                    f"Failed to load data into {table_name}"
                )

            return nrows

        finally:
            db.close("snowflake")
