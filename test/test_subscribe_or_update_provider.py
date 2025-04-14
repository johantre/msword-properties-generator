import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
import shutil
from msword_properties_generator.main.subscribe_or_update_provider import main


class TestSubscribeOrUpdateProvider(unittest.TestCase):
    """Test suite for subscribe_or_update_provider.py"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock environment variables
        self.env_patcher = patch.dict('os.environ', {
            'INPUT_LEVERANCIEREMAIL': 'test@example.com',
            'INPUT_LEVERANCIERNAAM': 'Test Provider',
            'INPUT_LEVERANCIERSTAD': 'Test City',
            'INPUT_LEVERANCIERSTRAAT': 'Test Street',
            'INPUT_LEVERANCIERPOSTADRES': 'Test Postal',
            'INPUT_LEVERANCIERKANDIDAAT': 'Test Candidate',
            'INPUT_LEVERANCIEROPGEMAAKTTE': 'Test Date',
            'INPUT_LEVERANCIERHOEDANIGHEID': 'Directe Freelancer',
            'INPUT_LEVERANCIERURLSIGNATUREIMAGE': 'https://example.com/signature.jpg',
            'LOG_LEVEL': 'INFO',
            'HASHING_KEY': 'test_hash_key',
            'ENCRYPTION_KEY': 'test_encryption_key',
            'GOOGLE_CLIENT_ID': 'test_google_client_id',
            'GOOGLE_CLIENT_SECRET': 'test_google_client_secret',
            'GOOGLE_REFRESH_TOKEN': 'test_google_refresh_token',
            'DROPBOX_APP_KEY': 'test_dropbox_app_key',
            'DROPBOX_APP_SECRET': 'test_dropbox_app_secret',
            'DROPBOX_REFRESH_TOKEN': 'test_dropbox_refresh_token'
        })
        self.env_patcher.start()
        
        # Mock the database functions
        self.db_patcher = patch('msword_properties_generator.main.subscribe_or_update_provider.init_db')
        self.mock_init_db = self.db_patcher.start()
        
        self.insert_patcher = patch('msword_properties_generator.main.subscribe_or_update_provider.insert_into_db')
        self.mock_insert_into_db = self.insert_patcher.start()
        
        self.update_patcher = patch('msword_properties_generator.main.subscribe_or_update_provider.update_provider')
        self.mock_update_provider = self.update_patcher.start()
        
        self.get_patcher = patch('msword_properties_generator.main.subscribe_or_update_provider.get_leverancier_dict')
        self.mock_get_leverancier_dict = self.get_patcher.start()
        
        # Mock the download functions
        self.download_patcher = patch('msword_properties_generator.main.subscribe_or_update_provider.download_image')
        self.mock_download_image = self.download_patcher.start()
        
        # Mock the logging
        self.logging_patcher = patch('msword_properties_generator.main.subscribe_or_update_provider.logging')
        self.mock_logging = self.logging_patcher.start()
        
        # Mock the close_db function
        self.close_patcher = patch('msword_properties_generator.main.subscribe_or_update_provider.close_db_commit_push')
        self.mock_close_db = self.close_patcher.start()
        
        # Set up the mock returns
        self.mock_get_leverancier_dict.return_value = None  # Provider not found initially
        
    def tearDown(self):
        """Clean up after tests"""
        # Stop all patchers
        self.env_patcher.stop()
        self.db_patcher.stop()
        self.insert_patcher.stop()
        self.update_patcher.stop()
        self.get_patcher.stop()
        self.download_patcher.stop()
        self.logging_patcher.stop()
        self.close_patcher.stop()
        
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_new_provider_insertion(self):
        """Test inserting a new provider"""
        # Call the main function
        main()
        
        # Verify the function calls
        self.mock_init_db.assert_called_once()
        self.mock_get_leverancier_dict.assert_called_once()
        self.mock_insert_into_db.assert_called_once()
        self.mock_download_image.assert_called_once()
        self.mock_close_db.assert_called_once()
        
        # Verify the provider was not updated (since it's new)
        self.mock_update_provider.assert_not_called()
    
    def test_existing_provider_update(self):
        """Test updating an existing provider"""
        # Set up the mock to return an existing provider
        self.mock_get_leverancier_dict.return_value = {
            "LeverancierNaam": "Existing Provider",
            "LeverancierEmail": "test@example.com"
        }
        
        # Call the main function
        main()
        
        # Verify the function calls
        self.mock_init_db.assert_called_once()
        self.mock_get_leverancier_dict.assert_called_once()
        self.mock_update_provider.assert_called_once()
        self.mock_download_image.assert_called_once()
        self.mock_close_db.assert_called_once()
        
        # Verify the provider was not inserted (since it exists)
        self.mock_insert_into_db.assert_not_called()
    
    def test_download_image_error(self):
        """Test handling download image error"""
        # Make download_image raise an exception
        self.mock_download_image.side_effect = Exception("Download error")
        
        # Call the main function
        main()
        
        # Verify error was logged
        self.mock_logging.error.assert_called()
        
        # Verify the provider was still inserted/updated
        self.assertTrue(self.mock_insert_into_db.called or self.mock_update_provider.called)
    
    def test_database_error(self):
        """Test handling database error"""
        # Make init_db raise an exception
        self.mock_init_db.side_effect = Exception("Database error")
        
        # Call the main function
        main()
        
        # Verify error was logged
        self.mock_logging.error.assert_called()
        
        # Verify the provider was not inserted/updated
        self.mock_insert_into_db.assert_not_called()
        self.mock_update_provider.assert_not_called()


if __name__ == '__main__':
    unittest.main() 