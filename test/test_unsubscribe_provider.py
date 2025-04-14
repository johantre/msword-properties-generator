import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
import shutil

from msword_properties_generator.main.unsubscribe_provider import main


class TestUnsubscribeProvider(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for the test database
        self.test_dir = tempfile.mkdtemp()
        
        # Mock the database functions
        self.db_patcher = patch('msword_properties_generator.main.unsubscribe_provider.init_db')
        self.remove_provider_patcher = patch('msword_properties_generator.main.unsubscribe_provider.remove_provider')
        self.commit_db_patcher = patch('msword_properties_generator.main.unsubscribe_provider.commit_db')
        self.close_db_patcher = patch('msword_properties_generator.main.unsubscribe_provider.close_db_commit_push')
        self.remove_image_patcher = patch('msword_properties_generator.main.unsubscribe_provider.remove_from_image_folder_git_commit_push')
        self.setup_logging_patcher = patch('msword_properties_generator.main.unsubscribe_provider.setup_logging')
        
        # Start the patches
        self.mock_init_db = self.db_patcher.start()
        self.mock_remove_provider = self.remove_provider_patcher.start()
        self.mock_commit_db = self.commit_db_patcher.start()
        self.mock_close_db = self.close_db_patcher.start()
        self.mock_remove_image = self.remove_image_patcher.start()
        self.mock_setup_logging = self.setup_logging_patcher.start()
        
        # Create mock connection
        self.mock_conn = MagicMock()
        self.mock_init_db.return_value = self.mock_conn

    def tearDown(self):
        # Stop all patches
        self.db_patcher.stop()
        self.remove_provider_patcher.stop()
        self.commit_db_patcher.stop()
        self.close_db_patcher.stop()
        self.remove_image_patcher.stop()
        self.setup_logging_patcher.stop()
        
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    def test_successful_provider_unsubscribe(self):
        """Test successful provider unsubscribe process"""
        # Setup
        self.mock_remove_provider.return_value = True
        
        # Execute
        main()
        
        # Verify
        self.mock_setup_logging.assert_called_once()
        self.mock_init_db.assert_called_once()
        self.mock_remove_provider.assert_called_once_with(self.mock_conn)
        self.mock_remove_image.assert_called_once()
        self.mock_commit_db.assert_called_once_with(self.mock_conn)
        self.mock_close_db.assert_called_once_with(self.mock_conn)

    def test_provider_not_found(self):
        """Test when provider is not found"""
        # Setup
        self.mock_remove_provider.return_value = False
        
        # Execute
        main()
        
        # Verify
        self.mock_setup_logging.assert_called_once()
        self.mock_init_db.assert_called_once()
        self.mock_remove_provider.assert_called_once_with(self.mock_conn)
        self.mock_remove_image.assert_not_called()
        self.mock_commit_db.assert_called_once_with(self.mock_conn)
        self.mock_close_db.assert_called_once_with(self.mock_conn)

    def test_database_error(self):
        """Test database error handling"""
        # Setup
        self.mock_init_db.side_effect = Exception("Database error")
        
        # Execute and verify
        with self.assertRaises(Exception):
            main()
        
        # Verify
        self.mock_setup_logging.assert_called_once()
        self.mock_remove_provider.assert_not_called()
        self.mock_remove_image.assert_not_called()
        self.mock_commit_db.assert_not_called()
        self.mock_close_db.assert_not_called()

    def test_unsubscribe_error(self):
        """Test unsubscribe error handling"""
        # Setup
        self.mock_remove_provider.side_effect = Exception("Unsubscribe error")
        
        # Execute and verify
        with self.assertRaises(Exception):
            main()
        
        # Verify
        self.mock_setup_logging.assert_called_once()
        self.mock_init_db.assert_called_once()
        self.mock_remove_image.assert_not_called()
        self.mock_commit_db.assert_not_called()
        self.mock_close_db.assert_not_called()


if __name__ == '__main__':
    unittest.main() 