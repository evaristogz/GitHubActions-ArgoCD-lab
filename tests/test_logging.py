# tests/test_logging.py  
# Tests for logging configuration
from unittest.mock import patch, MagicMock


def test_logging_configuration():
    """Test that logging is configured correctly"""
    with patch('psycopg2.connect') as mock_connect, \
         patch('os.makedirs') as mock_makedirs, \
         patch('logging.FileHandler') as mock_file_handler, \
         patch('time.sleep'):
        
        # Mock file operations
        mock_makedirs.return_value = None
        mock_file_handler.return_value = MagicMock()
        
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn  
        mock_conn.cursor.return_value = mock_cursor
        
        # Import app to trigger logging setup
        from app import app as app_module
        
        # Verify logging components exist
        assert hasattr(app_module, 'logger')
        
        # Verify makedirs was called for log directory
        mock_makedirs.assert_called_with("/var/log/kc-visit-counter", exist_ok=True)


def test_logging_fallback_on_file_error():
    """Test logging fallback when file handler creation fails"""
    with patch('psycopg2.connect') as mock_connect, \
         patch('os.makedirs') as mock_makedirs, \
         patch('logging.FileHandler', side_effect=Exception("Cannot create file")), \
         patch('time.sleep'):
        
        mock_makedirs.return_value = None
        
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Import should still work even if file logging fails
        from app import app as app_module
        
        # Logger should still exist (console logging should work)
        assert hasattr(app_module, 'logger')