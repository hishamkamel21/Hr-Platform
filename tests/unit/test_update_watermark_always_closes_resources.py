import pytest
from unittest.mock import MagicMock, patch

from added_package.Helper import Helper
from added_package.Engine import DatabaseManager



@patch("added_package.Engine.DatabaseManager")
def test_update_watermark_always_closes_resources(mock_db_manager):

    mock_cursor = MagicMock()

    mock_cursor.execute.side_effect = Exception("Error")

    mock_db = MagicMock()
    mock_db.get_snowflake_cursor.return_value = mock_cursor

    mock_db_manager.return_value = mock_db

    with pytest.raises(Exception):
        Helper.update_watermark(
            target="customers",
            value="2024-01-01"
        )

    mock_cursor.close.assert_called_once()
    mock_db.close.assert_called_once_with("snowflake")