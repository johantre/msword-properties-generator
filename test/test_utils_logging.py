import unittest
from unittest.mock import patch, MagicMock
import logging
from datetime import datetime
import pytz
import os

from msword_properties_generator.utils.utils_logging import LocalTimezoneFormatter, setup_logging

class TestUtilsLogging(unittest.TestCase):
    def setUp(self):
        self.formatter = LocalTimezoneFormatter()
        self.record = MagicMock()
        self.record.created = datetime.now().timestamp()

    def test_formatter_timezone(self):
        """Test that the formatter uses the correct timezone"""
        formatted_time = self.formatter.formatTime(self.record)
        # Verify that the timezone is Europe/Amsterdam
        self.assertIn('Europe/Amsterdam', str(self.formatter.local_timezone))
        
    def test_formatter_custom_format(self):
        """Test that the formatter accepts custom date formats"""
        custom_format = "%Y-%m-%d"
        formatted_time = self.formatter.formatTime(self.record, datefmt=custom_format)
        # Verify the format matches our custom format
        self.assertEqual(len(formatted_time.split()), 1)  # Should be just the date

    @patch('logging.getLogger')
    @patch('logging.StreamHandler')
    def test_setup_logging_default_level(self, mock_handler, mock_get_logger):
        """Test setup_logging with default log level"""
        # Setup mocks
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Clear environment variable if it exists
        if 'LOG_LEVEL' in os.environ:
            del os.environ['LOG_LEVEL']
            
        setup_logging()
        
        # Verify logger was configured correctly
        mock_logger.setLevel.assert_called_with(logging.INFO)
        mock_logger.addHandler.assert_called_once()

    @patch('logging.getLogger')
    @patch('logging.StreamHandler')
    def test_setup_logging_custom_level(self, mock_handler, mock_get_logger):
        """Test setup_logging with custom log level"""
        # Setup mocks
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Set custom log level
        os.environ['LOG_LEVEL'] = 'DEBUG'
        
        setup_logging()
        
        # Verify logger was configured correctly
        mock_logger.setLevel.assert_called_with(logging.DEBUG)
        mock_logger.addHandler.assert_called_once()

    @patch('logging.getLogger')
    @patch('logging.StreamHandler')
    def test_setup_logging_clears_existing_handlers(self, mock_handler, mock_get_logger):
        """Test that setup_logging clears existing handlers"""
        # Setup mocks
        mock_logger = MagicMock()
        mock_logger.hasHandlers.return_value = True
        mock_get_logger.return_value = mock_logger
        
        setup_logging()
        
        # Verify handlers were cleared
        mock_logger.handlers.clear.assert_called_once()

if __name__ == '__main__':
    unittest.main() 