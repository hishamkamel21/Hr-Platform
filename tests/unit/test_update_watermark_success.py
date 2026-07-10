from unittest.mock import MagicMock, patch

from added_package.Helper import Helper


@patch("added_package.Engine.DatabaseManager")
def test_update_watermark_success(mock_db_manager):

    mock_cursor = MagicMock()

    mock_db = MagicMock()
    mock_db.get_snowflake_cursor.return_value = mock_cursor

    mock_db_manager.return_value = mock_db

    Helper.update_watermark(
        target="customers",
        value="2024-01-01"
    )

    mock_db.get_snowflake_cursor.assert_called_once_with(
        schema="metadata"
    )

    mock_cursor.execute.assert_called_once_with(
        """
            UPDATE watermarks
            SET Max_Timestamp = %s
            WHERE the_table = %s
            """,
        ("2024-01-01", "customers")
    )

    mock_cursor.connection.commit.assert_called_once()

    mock_cursor.close.assert_called_once()

    mock_db.close.assert_called_once_with("snowflake")