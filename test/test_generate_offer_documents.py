import unittest
from unittest.mock import patch, MagicMock, call
import os
import tempfile
import shutil
from msword_properties_generator.main.generate_offer_documents import _main, extract_combined_replacements


class TestGenerateOfferDocuments(unittest.TestCase):
    """Test suite for generate_offer_documents.py"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock the config
        self.config_patcher = patch('msword_properties_generator.main.generate_offer_documents.config')
        self.mock_config = self.config_patcher.start()
        self.mock_config.return_value = {
            "paths": {
                "xls_offers_customer": "test_data.xlsx",
                "xls_offers_customer_sheetname": "Sheet1"
            }
        }
        
        # Mock the logging setup
        self.logging_patcher = patch('msword_properties_generator.main.generate_offer_documents.setup_logging')
        self.mock_setup_logging = self.logging_patcher.start()
        
        # Mock the database and Excel functions
        self.db_patcher = patch('msword_properties_generator.main.generate_offer_documents.create_replacements_from_db')
        self.mock_create_replacements_from_db = self.db_patcher.start()
        
        self.xls_patcher = patch('msword_properties_generator.main.generate_offer_documents.create_replacements_from_xls')
        self.mock_create_replacements_from_xls = self.xls_patcher.start()
        
        # Mock document and PDF functions
        self.docx_patcher = patch('msword_properties_generator.main.generate_offer_documents.update_custom_properties_docx_structure')
        self.mock_update_docx = self.docx_patcher.start()
        
        self.pdf_patcher = patch('msword_properties_generator.main.generate_offer_documents.convert_to_pdf')
        self.mock_convert_to_pdf = self.pdf_patcher.start()
        
        # Mock email and Dropbox functions
        self.email_patcher = patch('msword_properties_generator.main.generate_offer_documents.send_email')
        self.mock_send_email = self.email_patcher.start()
        
        self.dropbox_patcher = patch('msword_properties_generator.main.generate_offer_documents.dropbox_upload')
        self.mock_dropbox_upload = self.dropbox_patcher.start()
        
        # Mock logging
        self.logging_module_patcher = patch('msword_properties_generator.main.generate_offer_documents.logging')
        self.mock_logging = self.logging_module_patcher.start()
        
        # Sample data for tests
        self.sample_provider_data = {
            "LeverancierNaam": "Test Provider",
            "LeverancierEmail": "provider@test.com",
            "LeverancierStad": "Test City"
        }
        
        self.sample_customer_data = {
            "KlantNaam": "Test Customer",
            "KlantJobTitle": "Test Job",
            "KlantJobReference": "REF123"
        }
        
        # Set up the mock returns
        self.mock_create_replacements_from_db.return_value = self.sample_provider_data
        self.mock_create_replacements_from_xls.return_value = self.sample_customer_data
        self.mock_update_docx.return_value = os.path.join(self.temp_dir, "test_document")
        
    def tearDown(self):
        """Clean up after tests"""
        # Stop all patchers
        self.config_patcher.stop()
        self.logging_patcher.stop()
        self.db_patcher.stop()
        self.xls_patcher.stop()
        self.docx_patcher.stop()
        self.pdf_patcher.stop()
        self.email_patcher.stop()
        self.dropbox_patcher.stop()
        self.logging_module_patcher.stop()
        
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_extract_combined_replacements(self):
        """Test the extract_combined_replacements function"""
        # Call the function
        result = extract_combined_replacements(None)
        
        # Verify the function calls
        self.mock_create_replacements_from_db.assert_called_once_with(None)
        self.mock_create_replacements_from_xls.assert_called_once_with(
            "test_data.xlsx", "Sheet1", None
        )
        
        # Verify the result structure
        self.assertIn("prov_LeverancierNaam", result)
        self.assertIn("prov_LeverancierEmail", result)
        self.assertIn("cust_KlantNaam", result)
        self.assertIn("cust_KlantJobTitle", result)
        
        # Verify the values
        self.assertEqual(result["prov_LeverancierNaam"], "Test Provider")
        self.assertEqual(result["cust_KlantNaam"], "Test Customer")
    
    def test_main_without_optional_args(self):
        """Test the _main function without optional arguments"""
        # Call the function
        _main(verbose=False)
        
        # Verify the function calls
        self.mock_create_replacements_from_db.assert_called_once_with(None)
        self.mock_create_replacements_from_xls.assert_called_once()
        self.mock_update_docx.assert_called_once()
        self.mock_convert_to_pdf.assert_called_once()
        self.mock_send_email.assert_called_once()
        self.mock_dropbox_upload.assert_called_once()
    
    def test_main_with_optional_args(self):
        """Test the _main function with optional arguments"""
        # Prepare optional arguments
        optional_args = {
            "LeverancierEmail": "custom@test.com",
            "UploadDropbox": "false"
        }
        
        # Call the function
        _main(verbose=True, optional_args=optional_args)
        
        # Verify the function calls
        self.mock_create_replacements_from_db.assert_called_once_with(optional_args)
        self.mock_create_replacements_from_xls.assert_called_once()
        self.mock_update_docx.assert_called_once()
        self.mock_convert_to_pdf.assert_called_once()
        self.mock_send_email.assert_called_once()
        
        # Verify Dropbox upload was not called (UploadDropbox = false)
        self.mock_dropbox_upload.assert_not_called()
    
    def test_main_with_dropbox_error(self):
        """Test the _main function with Dropbox upload error"""
        # Make Dropbox upload raise an exception
        self.mock_dropbox_upload.side_effect = Exception("Dropbox error")
        
        # Call the function
        _main(verbose=False)
        
        # Verify error was logged
        self.mock_logging.error.assert_called()
    
    def test_main_with_email_error(self):
        """Test the _main function with email sending error"""
        # Make email sending raise an exception
        self.mock_send_email.side_effect = Exception("Email error")
        
        # Call the function
        _main(verbose=False)
        
        # Verify error was logged
        self.mock_logging.error.assert_called()
    
    def test_main_with_document_error(self):
        """Test the _main function with document generation error"""
        # Make document update raise an exception
        self.mock_update_docx.side_effect = Exception("Document error")
        
        # Call the function
        _main(verbose=False)
        
        # Verify error was logged
        self.mock_logging.error.assert_called()
    
    def test_main_with_pdf_error(self):
        """Test the _main function with PDF conversion error"""
        # Make PDF conversion raise an exception
        self.mock_convert_to_pdf.side_effect = Exception("PDF error")
        
        # Call the function
        _main(verbose=False)
        
        # Verify error was logged
        self.mock_logging.error.assert_called()


if __name__ == '__main__':
    unittest.main() 