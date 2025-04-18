from unittest.mock import patch
from cryptography.fernet import Fernet
import unittest
import tempfile
import os


from msword_properties_generator.utils.utils_hash_encrypt import (
    get_encryption_key,
    get_hash_key,
    get_cipher_suite,
    encrypt,
    decrypt,
    hash,
    encrypt_image,
    decrypt_image
)

class TestUtilsHashEncrypt(unittest.TestCase):
    def setUp(self):
        # Create temporary directory for file operations
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock environment variables
        self.env_patcher = patch.dict('os.environ', {
            'ENCRYPTION_KEY': Fernet.generate_key().decode(),
            'HASHING_KEY': 'test_hash_key'
        })
        self.env_patcher.start()
        
        # Create test files
        self.test_input_file = os.path.join(self.temp_dir, 'test_input.png')
        self.test_output_file = os.path.join(self.temp_dir, 'test_output.enc')
        self.test_decrypted_file = os.path.join(self.temp_dir, 'test_decrypted.png')
        
        # Create a simple test image
        with open(self.test_input_file, 'wb') as f:
            f.write(b'test image data')

    def tearDown(self):
        # Clean up temporary files
        for file in [self.test_input_file, self.test_output_file, self.test_decrypted_file]:
            if os.path.exists(file):
                os.remove(file)
        os.rmdir(self.temp_dir)
        
        # Stop all patchers
        self.env_patcher.stop()

    def test_get_encryption_key(self):
        key = get_encryption_key()
        self.assertIsInstance(key, str)
        self.assertTrue(len(key) > 0)

    def test_get_hash_key(self):
        key = get_hash_key()
        self.assertEqual(key, 'test_hash_key')

    def test_get_cipher_suite(self):
        cipher_suite = get_cipher_suite()
        self.assertIsInstance(cipher_suite, Fernet)

    @patch('msword_properties_generator.utils.utils_hash_encrypt.logging')
    def test_encrypt_decrypt_string(self, mock_logging):
        test_string = "test sensitive data"
        
        # Encrypt
        encrypted = encrypt(test_string)
        self.assertIsInstance(encrypted, str)
        self.assertNotEqual(encrypted, test_string)
        mock_logging.debug.assert_called_with("🔒 Sensitive data encrypted successfully. Processing further...")
        
        # Decrypt
        decrypted = decrypt(encrypted)
        self.assertEqual(decrypted, test_string)
        mock_logging.debug.assert_called_with("🔓 Sensitive data decrypted successfully. Processing further...")

    @patch('msword_properties_generator.utils.utils_hash_encrypt.logging')
    def test_hash_string(self, mock_logging):
        test_string = "test@example.com"
        hashed = hash(test_string)
        
        self.assertIsInstance(hashed, str)
        self.assertNotEqual(hashed, test_string)
        self.assertEqual(len(hashed), 64)  # SHA-256 produces 64 hex characters
        mock_logging.debug.assert_called_with("🆔 Sensitive data hashed successfully. Processing further...")

    @patch('msword_properties_generator.utils.utils_hash_encrypt.logging')
    def test_encrypt_image(self, mock_logging):
        encrypt_image(self.test_input_file, self.test_output_file)
        
        self.assertTrue(os.path.exists(self.test_output_file))
        self.assertGreater(os.path.getsize(self.test_output_file), 0)
        mock_logging.debug.assert_called_with("🔒 Sensitive image encrypted successfully. Processing further...")

    @patch('msword_properties_generator.utils.utils_hash_encrypt.logging')
    def test_decrypt_image(self, mock_logging):
        # First encrypt the image
        encrypt_image(self.test_input_file, self.test_output_file)
        
        # Then decrypt it
        decrypt_image(self.test_output_file, self.test_decrypted_file)
        
        self.assertTrue(os.path.exists(self.test_decrypted_file))
        self.assertGreater(os.path.getsize(self.test_decrypted_file), 0)
        
        # Verify the decrypted content matches the original
        with open(self.test_input_file, 'rb') as f1, open(self.test_decrypted_file, 'rb') as f2:
            self.assertEqual(f1.read(), f2.read())
        
        mock_logging.debug.assert_called_with("🔓 Sensitive image decrypted successfully. Processing further...")

    def test_encrypt_image_invalid_input(self):
        with self.assertRaises(FileNotFoundError):
            encrypt_image('nonexistent.png', self.test_output_file)

    def test_decrypt_image_invalid_input(self):
        with self.assertRaises(FileNotFoundError):
            decrypt_image('nonexistent.enc', self.test_decrypted_file)

    def test_decrypt_image_invalid_format(self):
        # Create an invalid encrypted file
        with open(self.test_output_file, 'wb') as f:
            f.write(b'invalid encrypted data')
        
        with self.assertRaises(Exception):
            decrypt_image(self.test_output_file, self.test_decrypted_file)

if __name__ == '__main__':
    unittest.main() 