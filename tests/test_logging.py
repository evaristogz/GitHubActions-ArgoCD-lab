# tests/test_logging.py  
# Tests for logging configuration
import pytest
import os
from unittest.mock import patch, MagicMock


@patch('logging.FileHandler')
@patch('os.makedirs')
def test_logging_configuration(mock_makedirs, mock_file_handler):
    """Test that logging is configured correctly"""
    
    # Mock file operations
    mock_makedirs.return_value = None
    mock_file_handler.return_value = MagicMock()
    
    # Mock psycopg2 to avoid database connection during import
    with patch('psycopg2.connect') as mock_connect:
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


@patch('logging.FileHandler', side_effect=Exception("Cannot create file"))
@patch('os.makedirs')  
def test_logging_fallback_on_file_error(mock_makedirs, mock_file_handler):
    """Test logging fallback when file handler creation fails"""
    
    mock_makedirs.return_value = None
    
    # Mock psycopg2 to avoid database connection during import
    with patch('psycopg2.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Import should still work even if file logging fails
        from app import app as app_module
        
        # Logger should still exist (console logging should work)
        assert hasattr(app_module, 'logger')