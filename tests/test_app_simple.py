# tests/test_app_simple.py
# Simple tests to ensure code coverage for the Flask application
import os
import sys
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime


@patch('psycopg2.connect')  
@patch('os.makedirs')
@patch('logging.FileHandler')
def test_app_module_imports_and_basic_functionality(mock_file_handler, mock_makedirs, mock_connect):
    """Test that we can import the app module and basic functionality works"""
    
    # Mock database connection
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Mock file handler to avoid file system operations
    mock_file_handler.return_value = Mock()
    mock_makedirs.return_value = None
    
    # Set test environment
    test_env = {
        'DB_NAME': 'testdb',
        'DB_USER': 'testuser',
        'DB_PASSWORD': 'testpass', 
        'DB_HOST': 'localhost',
        'DB_PORT': '5432'
    }
    
    with patch.dict(os.environ, test_env):
        # Clear module cache to ensure fresh import
        modules_to_clear = [key for key in sys.modules.keys() if key.startswith('app')]
        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]
        
        # Import the app module - this should execute most of the code
        from app import app as app_module
        
        # Verify basic attributes exist
        assert hasattr(app_module, 'app')
        assert hasattr(app_module, 'DB_CONFIG')
        assert hasattr(app_module, 'logger')
        
        # Verify configuration
        assert app_module.DB_CONFIG['dbname'] == 'testdb'
        assert app_module.DB_CONFIG['user'] == 'testuser'
        
        # Verify Flask app was created
        assert app_module.app is not None
        assert app_module.app.name == 'app.app'


@patch('psycopg2.connect')
def test_main_route_functionality(mock_connect):
    """Test the main route with mocked database"""
    
    # Mock database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Mock database responses
    mock_cursor.fetchone.return_value = [3]  # Total visits count
    mock_cursor.fetchall.return_value = [
        (1, datetime(2025, 10, 24, 10, 0, 0)),
        (2, datetime(2025, 10, 24, 11, 0, 0)),
        (3, datetime(2025, 10, 24, 12, 0, 0))
    ]
    
    # Import fresh module
    from app import app as app_module
    
    # Create test client
    client = app_module.app.test_client()
    
    # Replace the global connection and cursor in the module
    with patch.object(app_module, 'conn', mock_conn), \
         patch.object(app_module, 'cursor', mock_cursor):
        
        # Make request to main route
        response = client.get('/')
        
        # Verify response
        assert response.status_code == 200
        assert b'Total de visitas' in response.data
        assert b'3' in response.data
        assert b'ltimas visitas' in response.data
        
        # Verify database operations were called
        assert mock_cursor.execute.call_count >= 2  # INSERT and SELECT calls
        mock_conn.commit.assert_called()


@patch('psycopg2.connect')
def test_database_error_handling(mock_connect):
    """Test error handling when database operations fail"""
    
    # Mock database connection that raises an exception
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Make cursor.execute raise an exception
    mock_cursor.execute.side_effect = Exception("Database error")
    
    from app import app as app_module
    
    client = app_module.app.test_client()
    
    with patch.object(app_module, 'conn', mock_conn), \
         patch.object(app_module, 'cursor', mock_cursor):
        
        # Make request - should handle the error
        response = client.get('/')
        
        # Should return 500 error
        assert response.status_code == 500
        assert b'Error interno del servidor' in response.data