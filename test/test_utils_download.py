from unittest.mock import patch, MagicMock
import unittest
import os


from msword_properties_generator.utils.utils_download import (
    detect_host,
    download_image,
    get_google_drive_service,
    get_dropbox_service
)

class TestUtilsDownload(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_files')
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Set up environment variables
        self.env_vars = {
            'GOOGLE_CLIENT_ID': 'test_google_client_id',
            'GOOGLE_CLIENT_SECRET': 'test_google_client_secret',
            'GOOGLE_REFRESH_TOKEN': 'test_google_refresh_token',
            'DROPBOX_APP_KEY': 'test_dropbox_app_key',
            'DROPBOX_APP_SECRET': 'test_dropbox_app_secret',
            'DROPBOX_REFRESH_TOKEN': 'test_dropbox_refresh_token'
        }
        
        # Set up module-level variable patches
        self.patches = [
            patch('msword_properties_generator.utils.utils_download.GOOGLE_CLIENT_ID', 'test_google_client_id'),
            patch('msword_properties_generator.utils.utils_download.GOOGLE_CLIENT_SECRET', 'test_google_client_secret'),
            patch('msword_properties_generator.utils.utils_download.GOOGLE_REFRESH_TOKEN', 'test_google_refresh_token'),
            patch('msword_properties_generator.utils.utils_download.DROPBOX_APP_KEY', 'test_dropbox_app_key'),
            patch('msword_properties_generator.utils.utils_download.DROPBOX_APP_SECRET', 'test_dropbox_app_secret'),
            patch('msword_properties_generator.utils.utils_download.DROPBOX_REFRESH_TOKEN', 'test_dropbox_refresh_token')
        ]
        for p in self.patches:
            p.start()
            
    def tearDown(self):
        # Clean up test files
        if os.path.exists(self.test_dir):
            for file in os.listdir(self.test_dir):
                try:
                    os.remove(os.path.join(self.test_dir, file))
                except PermissionError:
                    pass  # Ignore files that are still in use
            try:
                os.rmdir(self.test_dir)
            except OSError:
                pass  # Ignore if directory is not empty
            
        # Stop all patches
        for p in self.patches:
            p.stop()

    def test_detect_host(self):
        test_cases = [
            ('https://drive.google.com/file/d/1234567890/view', 'gdrive'),
            ('https://www.dropbox.com/s/1234567890/file.jpg', 'dropbox'),
            ('https://uguu.se', 'uguu'),
            ('https://d.uguu.se', 'uguu'),
            ('https://example.com/file.jpg', 'unknown')
        ]

        for url, expected_host in test_cases:
            with self.subTest(url=url):
                self.assertEqual(detect_host(url), expected_host)

    @patch('msword_properties_generator.utils.utils_download.build')
    @patch('msword_properties_generator.utils.utils_download.Credentials')
    def test_get_google_drive_service(self, mock_credentials_class, mock_build):
        mock_creds = MagicMock()
        mock_credentials_class.return_value = mock_creds
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        # Call the function
        service = get_google_drive_service()
        
        # Verify credentials were created correctly
        mock_credentials_class.assert_called_once_with(
            token=None,
            refresh_token='test_google_refresh_token',
            token_uri='https://oauth2.googleapis.com/token',
            client_id='test_google_client_id',
            client_secret='test_google_client_secret'
        )
        
        # Verify credentials were refreshed
        mock_creds.refresh.assert_called_once()
        
        # Verify service was built
        mock_build.assert_called_once_with('drive', 'v3', credentials=mock_creds)
        
        # Verify returned service
        self.assertEqual(service, mock_service)

    @patch('msword_properties_generator.utils.utils_download.dropbox.Dropbox')
    def test_get_dropbox_service(self, mock_dropbox):
        mock_client = MagicMock()
        mock_dropbox.return_value = mock_client
        
        # Call the function
        service = get_dropbox_service()
        
        # Verify Dropbox client was initialized correctly
        mock_dropbox.assert_called_once_with(
            oauth2_refresh_token='test_dropbox_refresh_token',
            app_key='test_dropbox_app_key',
            app_secret='test_dropbox_app_secret'
        )
        
        # Verify returned service
        self.assertEqual(service, mock_client)

    @patch('msword_properties_generator.utils.utils_download.get_google_drive_service')
    def test_download_image_google_drive(self, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        mock_request = MagicMock()
        mock_service.files().get_media.return_value = mock_request
        
        # Create test file path
        test_file = os.path.join(self.test_dir, 'test.jpg')
        
        # Mock the MediaIoBaseDownload
        mock_downloader = MagicMock()
        mock_status = MagicMock()
        mock_status.progress.return_value = 1.0
        mock_downloader.next_chunk.side_effect = [(mock_status, False), (mock_status, True)]
        
        with patch('msword_properties_generator.utils.utils_download.MediaIoBaseDownload', return_value=mock_downloader):
            # Call the function
            download_image('https://drive.google.com/file/d/1234567890/view', test_file)
            
            # Verify service was used correctly
            mock_service.files().get_media.assert_called_once_with(fileId='1234567890')
            
            # Verify download was completed
            self.assertEqual(mock_downloader.next_chunk.call_count, 2)
            
            # Verify file was created
            self.assertTrue(os.path.exists(test_file))

    @patch('msword_properties_generator.utils.utils_download.get_dropbox_service')
    def test_download_image_dropbox(self, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        mock_metadata = MagicMock()
        mock_metadata.name = 'test.jpg'
        mock_response = MagicMock()
        mock_response.content = b'test content'
        
        mock_service.sharing_get_shared_link_file.return_value = (mock_metadata, mock_response)
        
        # Create test file
        test_file = os.path.join(self.test_dir, 'test.jpg')
        
        # Call the function
        download_image('https://www.dropbox.com/s/1234567890/test.jpg', test_file)
        
        # Verify service was used correctly
        mock_service.sharing_get_shared_link_file.assert_called_once()

    @patch('requests.get')
    def test_download_image_uguu(self, mock_get):
        mock_response = MagicMock()
        mock_response.url = 'https://d.uguu.se/1234567890.png'
        mock_response.content = b'test content'
        mock_get.return_value = mock_response
        
        # Create test file
        test_file = os.path.join(self.test_dir, 'test.jpg')
        
        # Call the function
        download_image('https://d.uguu.se/1234567890.png', test_file)
        
        # Verify request was made
        mock_get.assert_called_once()

    def test_download_image_invalid_host(self):
        test_file = os.path.join(self.test_dir, 'test.jpg')
        
        # Call the function and verify it raises ValueError
        with self.assertRaises(ValueError):
            download_image('https://example.com/file.jpg', test_file)

if __name__ == '__main__':
    unittest.main() 