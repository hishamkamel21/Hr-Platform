from unittest.mock import MagicMock, patch

from added_package.Helper import Helper


@patch("added_package.Engine.DatabaseManager")
def test_get_watermark_success(mock_db_manager):

    mock_cursor = MagicMock()

    mock_cursor.fetchone.return_value = (
        "2024-01-01 10:00:00",
        "updated_at"
    )

    mock_db = MagicMock()
    mock_db.get_snowflake_cursor.return_value = mock_cursor

    mock_db_manager.return_value = mock_db

    timestamp, column = Helper.get_watermark(
        target="customers",
        schema="metadata"
    )

    assert timestamp == "2024-01-01 10:00:00"
    assert column == "updated_at"

    mock_db.get_snowflake_cursor.assert_called_once_with(
        schema="metadata"
    )

    mock_cursor.execute.assert_called_once_with(
        """
            SELECT max_timestamp, watermark_col
            FROM watermarks
            WHERE the_table = %s
            """,
        ("customers",)
    )

    mock_cursor.fetchone.assert_called_once()

    mock_cursor.close.assert_called_once()

    mock_db.close.assert_called_once_with("snowflake") 