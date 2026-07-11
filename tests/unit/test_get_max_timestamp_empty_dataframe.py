import pandas as pd

from added_package.Helper import Helper


def test_get_max_timestamp_empty_dataframe():

    df = pd.DataFrame(columns=["updated_at"])

    result = Helper.get_max_timestamp(
        df=df,
        watermark_col="updated_at"
    )

    assert result is None