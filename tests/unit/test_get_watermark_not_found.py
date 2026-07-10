import pytest
from unittest.mock import MagicMock, patch

from added_package.Helper import Helper
from added_package.Engine import DatabaseManager


@patch("added_package.Engine.DatabaseManager")
def test_get_watermark_not_found(mock_db_manager):

    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None

    mock_db = MagicMock()
    mock_db.get_snowflake_cursor.return_value = mock_cursor

    mock_db_manager.return_value = mock_db

    with pytest.raises(Exception):
        Helper.get_watermark("customers")