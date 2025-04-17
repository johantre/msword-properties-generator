from msword_properties_generator.utils.utils_dropbox import dropbox_upload, get_dbx_client
from unittest.mock import patch, MagicMock
from dropbox.exceptions import ApiError
import unittest
import os


class MockApiError(ApiError):
    def __init__(self):
        error = {
            '.tag': 'path',
            'reason': {'.tag': 'other'}
        }
        super().__init__(
            request_id='test_request_id',
            error=error,
            user_message_text='Test error',
            user_message_locale='en'
        )

class TestUtilsDropbox(unittest.TestCase):
    def setUp(self):
        # Create test file
        self.test_file = os.path.join(os.path.dirname(__file__), 'test_file.txt')
        self.test_content = b'Test content'
        with open(self.test_file, 'wb') as f:
            f.write(self.test_content)
        
        # Set up environment variables
        os.environ['DROPBOX_APP_KEY'] = 'test_app_key'
        os.environ['DROPBOX_APP_SECRET'] = 'test_app_secret'
        os.environ['DROPBOX_REFRESH_TOKEN'] = 'test_refresh_token'
        
        # Set up config patcher
        self.config_patcher = patch('msword_properties_generator.utils.utils_dropbox.config', {
            'dropbox': {'dropbox_destination_folder': '/test_folder'}
        })
        self.mock_config = self.config_patcher.start()
        
    def tearDown(self):
        # Clean up test file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
            
        # Clean up environment variables
        for key in ['DROPBOX_APP_KEY', 'DROPBOX_APP_SECRET', 'DROPBOX_REFRESH_TOKEN']:
            if key in os.environ:
                del os.environ[key]
                
        # Stop config patcher
        self.config_patcher.stop()

    @patch('dropbox.Dropbox')
    def test_get_dbx_client(self, mock_dropbox):
        mock_client = MagicMock()
        mock_dropbox.return_value = mock_client
        
        client = get_dbx_client()
        self.assertEqual(client, mock_client)
        mock_dropbox.assert_called_once_with(
            oauth2_refresh_token='test_refresh_token',
            app_key='test_app_key',
            app_secret='test_app_secret'
        )

    @patch('dropbox.Dropbox')
    def test_dropbox_upload_success(self, mock_dropbox):
        mock_client = MagicMock()
        mock_dropbox.return_value = mock_client
        
        dropbox_upload([self.test_file])
        
        mock_client.files_upload.assert_called_once()
        args, kwargs = mock_client.files_upload.call_args
        self.assertEqual(args[0], self.test_content)
        self.assertEqual(args[1], '/test_folder/test_file.txt')

    @patch('dropbox.Dropbox')
    def test_dropbox_upload_api_error(self, mock_dropbox):
        mock_client = MagicMock()
        mock_dropbox.return_value = mock_client
        mock_client.files_upload.side_effect = MockApiError()
        
        dropbox_upload([self.test_file])
        
        mock_client.files_upload.assert_called_once()
        args, kwargs = mock_client.files_upload.call_args
        self.assertEqual(args[0], self.test_content)
        self.assertEqual(args[1], '/test_folder/test_file.txt')

    @patch('dropbox.Dropbox')
    def test_dropbox_upload_missing_file(self, mock_dropbox):
        mock_client = MagicMock()
        mock_dropbox.return_value = mock_client
        
        nonexistent_file = os.path.join(os.path.dirname(__file__), 'nonexistent.txt')
        with self.assertRaises(FileNotFoundError):
            dropbox_upload([nonexistent_file])
        
        mock_client.files_upload.assert_not_called()

if __name__ == '__main__':
    unittest.main() 