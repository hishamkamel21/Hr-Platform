import pandas as pd
import pytest

from added_package.Helper import Helper


def test_get_max_timestamp_invalid_column():

    df = pd.DataFrame({
        "created_at": pd.to_datetime([
            "2024-01-01"
        ])
    })

    with pytest.raises(KeyError):
        Helper.get_max_timestamp(
            df=df,
            watermark_col="updated_at"
        ) 

