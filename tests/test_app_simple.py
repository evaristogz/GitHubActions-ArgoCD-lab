# tests/test_app_simple.py
# Simple tests to ensure code coverage for the Flask application
import os
import sys
from unittest.mock import patch, MagicMock
from datetime import datetime


def test_basic_import():
    """Test basic import without database connection"""
    # Mock all external dependencies before importing
    with patch('psycopg2.connect') as mock_connect, \
         patch('os.makedirs'), \
         patch('logging.FileHandler'), \
         patch('time.sleep'):
        
        # Mock successful database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Clear module cache
        modules_to_clear = [key for key in sys.modules.keys() if key.startswith('app')]
        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]
        
        # Import the app module
        from app import app as app_module
        
        # Verify basic attributes exist
        assert hasattr(app_module, 'app')
        assert hasattr(app_module, 'DB_CONFIG') 
        assert hasattr(app_module, 'logger')
        
        # Verify Flask app was created
        assert app_module.app is not None


def test_route_with_successful_db():
    """Test the main route with successful database operations"""
    with patch('psycopg2.connect') as mock_connect, \
         patch('os.makedirs'), \
         patch('logging.FileHandler'), \
         patch('time.sleep'):
        
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock database responses
        mock_cursor.fetchone.return_value = [5]
        mock_cursor.fetchall.return_value = [
            (1, datetime(2025, 10, 24, 10, 0, 0)),
            (2, datetime(2025, 10, 24, 11, 0, 0))
        ]
        
        from app import app as app_module
        
        # Test the route
        with app_module.app.test_client() as client:
            response = client.get('/')
            
            assert response.status_code == 200
            assert b'Total de visitas' in response.data
            assert b'5' in response.data


def test_route_with_db_error():
    """Test route behavior when database operations fail"""
    with patch('psycopg2.connect') as mock_connect, \
         patch('os.makedirs'), \
         patch('logging.FileHandler'), \
         patch('time.sleep'):
        
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        from app import app as app_module
        
        # Mock cursor to raise exception during route execution
        with patch.object(app_module, 'cursor') as patched_cursor:
            patched_cursor.execute.side_effect = Exception("DB Error")
            
            with app_module.app.test_client() as client:
                response = client.get('/')
                
                assert response.status_code == 500
                assert b'Error interno del servidor' in response.data