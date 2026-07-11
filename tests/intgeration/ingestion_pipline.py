from added_package.Helper import Helper 
from added_package.Extract import Extract 
from added_package.Load import Load


def test_ingestion_pipline():
    
    the_timestamp , watermark_col = Helper.get_watermark(
        target="ids",
        schema="metadata"
    )

    df = Extract.from_postgres(
        table="ids",
        schema="test",
        max_timestamp=the_timestamp,
        watermark_column=watermark_col
    )

    df = Helper.add_metadata_col(df=df) 

    new_max_timestamp = Helper.get_max_timestamp(df=df, watermark_col=watermark_col)


    last_df = Helper.add_metadata_col(df=df)

    rows = Load.to_snowflake(
        df=last_df,
        table_name="IDS",
        schema="TEST"
    )

    if rows != 10 :
        raise ValueError(
            "the intgertion_test falied"
        )
    else :
        
        Helper.update_watermark(
            target="ids",
            value=new_max_timestamp
        )

        print("the test succseded")


if __name__ == '__main__':

    test_ingestion_pipline() 




