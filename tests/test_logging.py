# tests/test_logging.py  
# Tests for logging configuration
from unittest.mock import patch, MagicMock, Mock


def test_logging_setup():
    """Test that logging is set up during module import"""
    with patch('psycopg2.connect', return_value=MagicMock()), \
         patch('time.sleep'), \
         patch('os.makedirs') as mock_makedirs, \
         patch('logging.FileHandler', return_value=Mock()):
        
        # Import should trigger logging setup
        import app.app
        
        # Verify logging directory creation was attempted
        mock_makedirs.assert_called_with("/var/log/kc-visit-counter", exist_ok=True)