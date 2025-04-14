import unittest
from unittest.mock import patch, MagicMock
import sys
from io import StringIO
from msword_properties_generator.main.generate_offer_documents import _main


class TestGenerateOfferDocumentsCLI(unittest.TestCase):
    """Test suite for the command-line interface of generate_offer_documents.py"""

    def setUp(self):
        """Set up test fixtures"""
        # Mock the _main function
        self.main_patcher = patch('msword_properties_generator.main.generate_offer_documents._main')
        self.mock_main = self.main_patcher.start()
        
        # Capture stdout
        self.stdout = StringIO()
        self.stderr = StringIO()
        self.stdout_patcher = patch('sys.stdout', self.stdout)
        self.stderr_patcher = patch('sys.stderr', self.stderr)
        self.stdout_patcher.start()
        self.stderr_patcher.start()
        
        # Mock argparse
        self.argparse_patcher = patch('msword_properties_generator.main.generate_offer_documents.argparse')
        self.mock_argparse = self.argparse_patcher.start()
        
        # Create a mock ArgumentParser
        self.mock_parser = MagicMock()
        self.mock_argparse.ArgumentParser.return_value = self.mock_parser
        
        # Create a mock Namespace
        self.mock_args = MagicMock()
        self.mock_parser.parse_args.return_value = self.mock_args
        
        # Import the module after patching
        with patch.dict('sys.modules', {'msword_properties_generator.main.generate_offer_documents': MagicMock()}):
            import importlib
            self.module = importlib.import_module('msword_properties_generator.main.generate_offer_documents')
    
    def tearDown(self):
        """Clean up after tests"""
        # Stop all patchers
        self.main_patcher.stop()
        self.stdout_patcher.stop()
        self.stderr_patcher.stop()
        self.argparse_patcher.stop()
    
    def test_main_called_with_verbose(self):
        """Test that _main is called with verbose=True when --verbose is used"""
        # Set up the mock args
        self.mock_args.verbose = True
        self.mock_args.klantNaam = None
        self.mock_args.klantJobTitle = None
        self.mock_args.klantJobReference = None
        
        # Run the script
        with patch.object(self.module, '__name__', '__main__'):
            self.module._main(verbose=True)
        
        # Verify _main was called with verbose=True
        self.mock_main.assert_called_once_with(verbose=True, optional_args=None)
    
    def test_main_called_with_optional_args(self):
        """Test that _main is called with optional_args when customer info is provided"""
        # Set up the mock args
        self.mock_args.verbose = False
        self.mock_args.klantNaam = "Test Customer"
        self.mock_args.klantJobTitle = "Test Job"
        self.mock_args.klantJobReference = "REF123"
        self.mock_args.leverancierEmail = "test@example.com"
        self.mock_args.uploadDropbox = "true"
        
        # Run the script
        with patch.object(self.module, '__name__', '__main__'):
            self.module._main(verbose=False, optional_args={
                'KlantNaam': "Test Customer",
                'KlantJobTitle': "Test Job",
                'KlantJobReference': "REF123",
                'LeverancierEmail': "test@example.com",
                'UploadDropbox': "true"
            })
        
        # Verify _main was called with the correct optional_args
        self.mock_main.assert_called_once_with(
            verbose=False,
            optional_args={
                'KlantNaam': "Test Customer",
                'KlantJobTitle': "Test Job",
                'KlantJobReference': "REF123",
                'LeverancierEmail': "test@example.com",
                'UploadDropbox': "true"
            }
        )
    
    def test_main_called_without_optional_args_when_customer_info_missing(self):
        """Test that _main is called without optional_args when customer info is missing"""
        # Set up the mock args
        self.mock_args.verbose = False
        self.mock_args.klantNaam = None
        self.mock_args.klantJobTitle = None
        self.mock_args.klantJobReference = None
        
        # Run the script
        with patch.object(self.module, '__name__', '__main__'):
            self.module._main(verbose=False)
        
        # Verify _main was called without optional_args
        self.mock_main.assert_called_once_with(verbose=False, optional_args=None)


if __name__ == '__main__':
    unittest.main() 