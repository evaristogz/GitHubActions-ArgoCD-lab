# tests/test_import_app.py
# Test to check if the main application module can be imported.
import pytest
import os
from unittest.mock import patch, MagicMock


def test_can_import_app():
    """Test basic import of app module"""
    import app
    assert hasattr(app, 'app')  # Flask app exists
    assert hasattr(app, 'DB_CONFIG')  # DB config exists


@patch('app.psycopg2.connect')
def test_app_initialization(mock_connect):
    """Test that app initializes correctly with mocked database"""
    # Mock database connection
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Set test environment variables
    test_env = {
        'DB_NAME': 'testdb',
        'DB_USER': 'testuser',
        'DB_PASSWORD': 'testpass',
        'DB_HOST': 'localhost',
        'DB_PORT': '5432'
    }
    
    with patch.dict(os.environ, test_env):
        # Reimport to trigger initialization with new env vars
        import importlib
        import app
        importlib.reload(app)
        
        # Verify database config was set correctly
        assert app.DB_CONFIG['dbname'] == 'testdb'
        assert app.DB_CONFIG['user'] == 'testuser'
        assert app.DB_CONFIG['host'] == 'localhost'


@patch('app.psycopg2.connect')
def test_flask_app_routes(mock_connect):
    """Test Flask app routes"""
    # Mock database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Mock database responses
    mock_cursor.fetchone.return_value = [5]  # Total visits
    mock_cursor.fetchall.return_value = [
        (1, '2025-10-24 10:00:00'),
        (2, '2025-10-24 11:00:00')
    ]
    
    # Import app after mocking
    import app
    
    # Test the Flask app
    with app.app.test_client() as client:
        # Mock the cursor and connection for this specific test
        with patch.object(app, 'cursor', mock_cursor), \
             patch.object(app, 'conn', mock_conn):
            
            response = client.get('/')
            
            # Verify response
            assert response.status_code == 200
            assert b'Total de visitas' in response.data
            assert b'5' in response.data  # Should show total visits
            
            # Verify database calls were made
            mock_cursor.execute.assert_called()
            mock_conn.commit.assert_called()
