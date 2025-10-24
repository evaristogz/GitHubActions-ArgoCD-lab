# tests/test_import_app.py
# Test to check if the main application module can be imported.
from unittest.mock import patch, MagicMock


def test_can_import_app():
    """Test basic import of app module"""
    with patch("psycopg2.connect", return_value=MagicMock()), patch(
        "time.sleep"
    ), patch("os.makedirs"), patch("logging.FileHandler") as mock_handler:

        # Configure handler mock
        mock_file_handler = MagicMock()
        mock_file_handler.level = 0
        mock_handler.return_value = mock_file_handler

        # Simple import test
        import app.app

        assert hasattr(app.app, "app")  # Flask app exists
        assert hasattr(app.app, "DB_CONFIG")  # DB config exists
