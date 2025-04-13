import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import tempfile
from pathlib import Path
import sys

# Add the src directory to the Python path
src_path = str(Path(__file__).resolve().parent.parent / 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from msword_properties_generator.utils.utils_mail import send_email
from msword_properties_generator.utils.util_config import config


class TestUtilsMail(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Create test files
        self.test_docx = os.path.join(self.test_dir, "test.docx")
        self.test_pdf = os.path.join(self.test_dir, "test.pdf")
        self.test_xlsx = os.path.join(self.test_dir, "test.xlsx")
        
        # Create dummy files
        with open(self.test_docx, 'w') as f:
            f.write("Dummy docx content")
        with open(self.test_pdf, 'w') as f:
            f.write("Dummy pdf content")
        with open(self.test_xlsx, 'w') as f:
            f.write("Dummy xlsx content")
        
        # Mock environment variable for email password
        self.env_patch = patch.dict('os.environ', {'APP_PASS_MAIL': 'test_password'})
        self.env_patch.start()
        
        # Mock config
        self.config_patch = patch('msword_properties_generator.utils.utils_mail.config', {
            "mail": {
                "mail_smtp_server": "smtp.test.com",
                "mail_smtp_port": 587,
                "mail_sender_email": "test@example.com"
            },
            "paths": {
                "base_document_name": "test_document"
            }
        })
        self.config_patch.start()

    def tearDown(self):
        # Clean up temporary files
        for file in [self.test_docx, self.test_pdf, self.test_xlsx]:
            if os.path.exists(file):
                os.remove(file)
        os.rmdir(self.test_dir)
        
        # Stop all patches
        self.env_patch.stop()
        self.config_patch.stop()

    @patch('smtplib.SMTP')
    def test_send_email_with_docx_and_pdf(self, mock_smtp):
        """Test sending email with docx and pdf attachments"""
        # Setup
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        
        # Test data
        generated_files = [self.test_docx, self.test_pdf]
        email_address = "recipient@example.com"
        provider_replacements = {
            "LeverancierNaam": "Test Provider",
            "LeverancierEmail": "provider@test.com",
            "LeverancierStad": "Test City",
            "LeverancierStraat": "Test Street",
            "LeverancierPostadres": "123 Test Address",
            "LeverancierKandidaat": "Test Candidate",
            "LeverancierOpgemaaktte": "Test Title",
            "LeverancierHoedanigheid": "Test Role"
        }
        customer_replacements = {
            "KlantNaam": "Test Customer",
            "KlantJobTitle": "Test Job",
            "KlantJobReference": "TEST-123"
        }
        
        # Execute
        send_email(generated_files, email_address, provider_replacements, customer_replacements)
        
        # Verify
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with("test@example.com", "test_password")
        mock_smtp_instance.send_message.assert_called_once()

    @patch('smtplib.SMTP')
    @patch('builtins.open', new_callable=mock_open)
    @patch('msword_properties_generator.utils.utils_mail.EmailMessage')
    def test_send_email_with_missing_file(self, mock_email_class, mock_file, mock_smtp):
        """Test sending email when one of the files is missing"""
        # Setup
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        
        # Create a simple mock for EmailMessage
        mock_email = MagicMock()
        mock_email_class.return_value = mock_email
        
        # Test data with a non-existent file
        generated_files = [self.test_docx, "nonexistent.pdf"]
        email_address = "recipient@example.com"
        provider_replacements = {
            "LeverancierNaam": "Test Provider",
            "LeverancierEmail": "provider@test.com",
            "LeverancierStad": "Test City",
            "LeverancierStraat": "Test Street",
            "LeverancierPostadres": "123 Test Address",
            "LeverancierKandidaat": "Test Candidate",
            "LeverancierOpgemaaktte": "Test Title",
            "LeverancierHoedanigheid": "Test Role"
        }
        customer_replacements = {
            "KlantNaam": "Test Customer",
            "KlantJobTitle": "Test Job",
            "KlantJobReference": "TEST-123"
        }
        
        # Execute
        send_email(generated_files, email_address, provider_replacements, customer_replacements)
        
        # Verify
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once()
        mock_smtp_instance.send_message.assert_called_once()

    @patch('smtplib.SMTP')
    @patch('logging.error')
    def test_send_email_smtp_error(self, mock_logging, mock_smtp):
        """Test handling of SMTP errors during email sending"""
        # Setup
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        mock_smtp_instance.send_message.side_effect = Exception("SMTP Error")
        
        # Test data
        generated_files = [self.test_docx, self.test_pdf]
        email_address = "recipient@example.com"
        provider_replacements = {
            "LeverancierNaam": "Test Provider",
            "LeverancierEmail": "provider@test.com",
            "LeverancierStad": "Test City",
            "LeverancierStraat": "Test Street",
            "LeverancierPostadres": "123 Test Address",
            "LeverancierKandidaat": "Test Candidate",
            "LeverancierOpgemaaktte": "Test Title",
            "LeverancierHoedanigheid": "Test Role"
        }
        customer_replacements = {
            "KlantNaam": "Test Customer",
            "KlantJobTitle": "Test Job",
            "KlantJobReference": "TEST-123"
        }
        
        # Execute
        send_email(generated_files, email_address, provider_replacements, customer_replacements)
        
        # Verify
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once()
        mock_smtp_instance.send_message.assert_called_once()
        mock_logging.assert_called_once()


if __name__ == '__main__':
    unittest.main() 