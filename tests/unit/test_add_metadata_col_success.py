import pandas as pd

from added_package.Helper import Helper


def test_add_metadata_col_success():

    df = pd.DataFrame({
        "id": [1, 2, 3]
    })

    result = Helper.add_metadata_col(df)

    assert "ingest_at" in result.columns
    assert len(result) == 3
    assert result["ingest_at"].notna().all()