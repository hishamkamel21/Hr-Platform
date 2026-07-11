import pytest
from unittest.mock import MagicMock, patch

from added_package.Helper import Helper
from added_package.Engine import DatabaseManager


@patch("added_package.Engine.DatabaseManager")
def test_get_watermark_database_error(mock_db_manager):

    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = Exception("Database Error")

    mock_db = MagicMock()
    mock_db.get_snowflake_cursor.return_value = mock_cursor

    mock_db_manager.return_value = mock_db

    with pytest.raises(Exception):
        Helper.get_watermark("customers") 