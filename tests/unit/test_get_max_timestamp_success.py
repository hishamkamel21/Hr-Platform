import pandas as pd

from added_package.Helper import Helper


def test_get_max_timestamp_success():

    df = pd.DataFrame({
        "updated_at": pd.to_datetime([
            "2024-01-01",
            "2024-01-05",
            "2024-01-03"
        ])
    })

    result = Helper.get_max_timestamp(
        df=df,
        watermark_col="updated_at"
    )

    assert result == pd.Timestamp("2024-01-05") 
    