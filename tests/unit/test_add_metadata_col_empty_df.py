import pandas as pd

from added_package.Helper import Helper


def test_add_metadata_col_empty_dataframe():

    df = pd.DataFrame()

    result = Helper.add_metadata_col(df)

    assert result is None