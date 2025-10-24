# tests/test_import_app.py
# Test to check if the main application module can be imported.
import os
import sys
from unittest.mock import patch, MagicMock
from datetime import datetime


def test_can_import_app():
    """Test basic import of app module"""
    with patch('psycopg2.connect') as mock_connect, \
         patch('os.makedirs'), \
         patch('logging.FileHandler'), \
         patch('time.sleep'):
        
        # Mock database to allow import
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        from app import app as app_module
        assert hasattr(app_module, 'app')  # Flask app exists
        assert hasattr(app_module, 'DB_CONFIG')  # DB config exists


def test_app_initialization():
    """Test that app initializes correctly with environment variables"""
    with patch('psycopg2.connect') as mock_connect, \
         patch('os.makedirs'), \
         patch('logging.FileHandler'), \
         patch('time.sleep'):
        
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
            # Clear any existing module cache
            modules_to_clear = [key for key in sys.modules.keys() if key.startswith('app')]
            for module in modules_to_clear:
                if module in sys.modules:
                    del sys.modules[module]
            
            # Import the app module
            from app import app as app_module
            
            # Verify database config was set correctly
            assert app_module.DB_CONFIG['dbname'] == 'testdb'
            assert app_module.DB_CONFIG['user'] == 'testuser'
            assert app_module.DB_CONFIG['host'] == 'localhost'


def test_flask_app_routes():
    """Test Flask app routes"""
    with patch('psycopg2.connect') as mock_connect, \
         patch('os.makedirs'), \
         patch('logging.FileHandler'), \
         patch('time.sleep'):
        
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock database responses
        mock_cursor.fetchone.return_value = [5]  # Total visits
        mock_cursor.fetchall.return_value = [
            (1, datetime(2025, 10, 24, 10, 0, 0)),
            (2, datetime(2025, 10, 24, 11, 0, 0))
        ]
        
        # Import app module
        from app import app as app_module
        
        # Test the Flask app
        with app_module.app.test_client() as client:
            response = client.get('/')
            
            # Verify response
            assert response.status_code == 200
            assert b'Total de visitas' in response.data
            assert b'5' in response.data  # Should show total visits
