from unittest.mock import patch
from PIL import Image
import unittest
import tempfile
import os


from msword_properties_generator.utils.utils_image import (
    get_image_and_encrypt_to_image_folder,
    get_image_and_decrypt_from_image_folder,
    remove_from_image_folder_git_commit_push,
    is_image_properly_decrypted,
    ImageDecryptionError
)

class TestUtilsImage(unittest.TestCase):
    def setUp(self):
        # Create temporary directories for testing
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.temp_dir, "test_image.png")
        
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='red')
        img.save(self.test_image_path)
        
        # Mock environment variables
        self.env_patcher = patch.dict('os.environ', {
            'INPUT_LEVERANCIEREMAIL': 'test@example.com',
            'INPUT_LEVERANCIERURLSIGNATUREIMAGE': 'https://example.com/image.png',
            'HMAC_SECRET': 'test_secret'  # Add HMAC secret for hashing
        })
        self.env_patcher.start()
        
        # Mock config
        self.config_patcher = patch('msword_properties_generator.utils.utils_image.config', {
            'paths': {
                'image_signature_folder': self.temp_dir
            }
        })
        self.config_patcher.start()

    def tearDown(self):
        # Clean up temporary files
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)
        os.rmdir(self.temp_dir)
        
        # Stop all patchers
        self.env_patcher.stop()
        self.config_patcher.stop()

    @patch('msword_properties_generator.utils.utils_image.download_image')
    @patch('msword_properties_generator.utils.utils_image.encrypt_image')
    @patch('msword_properties_generator.utils.utils_image.git_stage_commit_push')
    @patch('msword_properties_generator.utils.utils_image.hash')
    @patch('msword_properties_generator.utils.utils_image.is_image_properly_decrypted')
    def test_get_image_and_encrypt_to_image_folder_success(self, mock_is_proper, mock_hash, mock_git_push, mock_encrypt, mock_download):
        # Setup
        mock_hash.return_value = "hashed_email"
        mock_download.return_value = None
        mock_encrypt.return_value = None
        mock_git_push.return_value = None
        mock_is_proper.return_value = True
        
        # Execute
        get_image_and_encrypt_to_image_folder()
        
        # Verify
        mock_download.assert_called_once()
        mock_encrypt.assert_called_once()
        mock_git_push.assert_called_once()
        mock_hash.assert_called_with('test@example.com')

    @patch('msword_properties_generator.utils.utils_image.download_image')
    @patch('msword_properties_generator.utils.utils_image.hash')
    @patch('msword_properties_generator.utils.utils_image.logging')
    def test_get_image_and_encrypt_to_image_folder_download_failure(self, mock_logging, mock_hash, mock_download):
        # Setup
        mock_hash.return_value = "hashed_email"
        mock_download.side_effect = Exception("Download failed")
        
        # Execute and verify
        with patch('msword_properties_generator.utils.utils_image.tempfile.mkdtemp', return_value=self.temp_dir):
            with self.assertRaises(SystemExit) as cm:
                get_image_and_encrypt_to_image_folder()
            
            # Verify exit code and logging
            self.assertEqual(cm.exception.code, 1)
            mock_logging.error.assert_called_once_with(
                "📷🔴 Failed to download image from https://example.com/image.png. Error: Download failed"
            )

    @patch('msword_properties_generator.utils.utils_image.decrypt_image')
    @patch('msword_properties_generator.utils.utils_image.hash')
    @patch('msword_properties_generator.utils.utils_image.is_image_properly_decrypted')
    def test_get_image_and_decrypt_from_image_folder_success(self, mock_is_proper, mock_hash, mock_decrypt):
        # Setup
        mock_hash.return_value = "hashed_email"
        mock_decrypt.return_value = None
        mock_is_proper.return_value = True
        
        # Create a temporary file for the decrypted image
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, "decrypted_image.png")
        with open(temp_file, 'wb') as f:
            f.write(b'test image data')
        
        # Execute
        with patch('tempfile.mkdtemp', return_value=temp_dir):
            result = get_image_and_decrypt_from_image_folder("test@example.com")
        
        # Verify
        mock_decrypt.assert_called_once()
        self.assertTrue(os.path.dirname(result).startswith(tempfile.gettempdir()))
        
        # Cleanup
        os.remove(temp_file)
        os.rmdir(temp_dir)

    @patch('msword_properties_generator.utils.utils_image.decrypt_image')
    @patch('msword_properties_generator.utils.utils_image.hash')
    @patch('msword_properties_generator.utils.utils_image.is_image_properly_decrypted')
    @patch('msword_properties_generator.utils.utils_image.logging')
    def test_get_image_and_decrypt_from_image_folder_decryption_failure(self, mock_logging, mock_is_proper, mock_hash, mock_decrypt):
        # Setup
        mock_hash.return_value = "hashed_email"
        mock_decrypt.side_effect = Exception("Decryption failed")
        
        # Create a temporary directory for the test
        temp_dir = tempfile.mkdtemp()
        
        # Execute
        with patch('tempfile.mkdtemp', return_value=temp_dir):
            result = get_image_and_decrypt_from_image_folder("test@example.com")
        
        # Verify
        mock_logging.error.assert_called_once_with("📷❌ Failed to decrypt image: Decryption failed")
        self.assertEqual(result, "")
        
        # Cleanup
        os.rmdir(temp_dir)

    @patch('msword_properties_generator.utils.utils_image.hash')
    @patch('msword_properties_generator.utils.utils_image.git_stage_commit_push')
    def test_remove_from_image_folder_git_commit_push_success(self, mock_git_push, mock_hash):
        # Setup
        mock_hash.return_value = "hashed_email"
        mock_git_push.return_value = None
        
        # Create a file to remove
        test_file = os.path.join(self.temp_dir, "hashed_email")
        with open(test_file, 'w') as f:
            f.write("test")
        
        # Execute
        result = remove_from_image_folder_git_commit_push()
        
        # Verify
        self.assertFalse(os.path.exists(test_file))
        mock_git_push.assert_called_once()
        self.assertEqual(result, self.temp_dir)

    @patch('msword_properties_generator.utils.utils_image.hash')
    def test_remove_from_image_folder_git_commit_push_no_file(self, mock_hash):
        # Setup
        mock_hash.return_value = "nonexistent_file"
        
        # Execute
        result = remove_from_image_folder_git_commit_push()
        
        # Verify
        self.assertEqual(result, self.temp_dir)

    def test_is_image_properly_decrypted_success(self):
        # Execute
        result = is_image_properly_decrypted(self.test_image_path)
        
        # Verify
        self.assertTrue(result)

    def test_is_image_properly_decrypted_failure(self):
        # Create an invalid image file
        invalid_image_path = os.path.join(self.temp_dir, "invalid.png")
        with open(invalid_image_path, 'w') as f:
            f.write("not an image")
        
        # Execute and verify
        with self.assertRaises(ImageDecryptionError):
            is_image_properly_decrypted(invalid_image_path)
        
        # Cleanup
        os.remove(invalid_image_path)

if __name__ == '__main__':
    unittest.main() 