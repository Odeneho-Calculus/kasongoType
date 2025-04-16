"""
Unit tests for KasongoType desktop application
"""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock PyQt5 modules for testing without a GUI
sys.modules['PyQt5'] = MagicMock()
sys.modules['PyQt5.QtCore'] = MagicMock()
sys.modules['PyQt5.QtWidgets'] = MagicMock()
sys.modules['PyQt5.QtGui'] = MagicMock()
sys.modules['PyQt5.QtWebEngineWidgets'] = MagicMock()

# Import after mocking
from desktop.main import WebServer, check_server_status

class TestDesktopApp(unittest.TestCase):
    """Tests for the desktop application components"""

    @patch('desktop.main.requests.get')
    def test_check_server_status_success(self, mock_get):
        """Test checking server status when server is running"""
        # Configure mock to simulate successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = check_server_status()
        self.assertTrue(result)
        mock_get.assert_called_once()
    
    @patch('desktop.main.requests.get')
    def test_check_server_status_failure(self, mock_get):
        """Test checking server status when server is not running"""
        # Configure mock to simulate connection failure
        mock_get.side_effect = Exception("Connection failed")
        
        result = check_server_status()
        self.assertFalse(result)
        mock_get.assert_called_once()
    
    @patch('desktop.main.flask_app')
    def test_web_server_initialization(self, mock_flask_app):
        """Test WebServer thread initialization"""
        server = WebServer()
        self.assertTrue(server.daemon)  # Should be a daemon thread
    
    @patch('desktop.main.flask_app')
    def test_web_server_run(self, mock_flask_app):
        """Test WebServer thread run method"""
        server = WebServer()
        server.run()
        
        # Verify Flask app was run with correct parameters
        mock_flask_app.run.assert_called_once_with(
            host="127.0.0.1",
            port=5678,
            debug=False
        )

if __name__ == "__main__":
    unittest.main()