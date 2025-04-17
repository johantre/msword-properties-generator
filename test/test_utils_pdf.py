from msword_properties_generator.utils.utils_pdf import convert_to_pdf, convert_to_pdf_traditional
from unittest.mock import patch, MagicMock
from pathlib import Path
import subprocess
import unittest
import tempfile
import sys
import os


# Add the src directory to the Python path
src_path = str(Path(__file__).resolve().parent.parent / 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

class TestUtilsPdf(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.test_docx = os.path.join(self.test_dir, "test.docx")
        self.test_pdf = os.path.join(self.test_dir, "test.pdf")
        
        # Create a dummy docx file
        with open(self.test_docx, 'w') as f:
            f.write("Dummy docx content")
        
        # Mock the config paths
        self.config_patch = patch('msword_properties_generator.utils.utils_pdf.config', {
            "paths": {
                "output_path": self.test_dir
            }
        })
        self.config_patch.start()
        
        # Mock the docx2pdf convert function
        self.convert_patch = patch('msword_properties_generator.utils.utils_pdf.convert')
        self.mock_convert = self.convert_patch.start()

    def tearDown(self):
        # Clean up temporary files
        if os.path.exists(self.test_docx):
            os.remove(self.test_docx)
        if os.path.exists(self.test_pdf):
            os.remove(self.test_pdf)
        os.rmdir(self.test_dir)
        
        # Stop all patches
        self.config_patch.stop()
        self.convert_patch.stop()

    @patch('subprocess.run')
    def test_convert_to_pdf_soffice_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        
        # Execute
        convert_to_pdf(os.path.join(self.test_dir, "test"))
        
        # Verify
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], 'soffice')
        self.assertEqual(args[1], '--headless')
        self.assertEqual(args[2], '--convert-to')
        self.assertEqual(args[3], 'pdf')
        self.assertEqual(args[4], '--outdir')
        self.assertEqual(args[5], self.test_dir)
        self.assertTrue(args[6].endswith('test.docx'))

    @patch('subprocess.run')
    @patch('logging.error')
    def test_convert_to_pdf_soffice_not_found(self, mock_logging, mock_run):
        mock_run.side_effect = FileNotFoundError()
        
        # Execute
        convert_to_pdf(os.path.join(self.test_dir, "test"))
        
        # Verify
        mock_run.assert_called_once()  # Verify we tried to run soffice
        mock_logging.assert_called_once()  # Verify we logged an error

    @patch('subprocess.run')
    def test_convert_to_pdf_soffice_conversion_error(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "soffice")
        
        # Execute
        convert_to_pdf(os.path.join(self.test_dir, "test"))
        
        # Verify
        mock_run.assert_called_once()

    def test_convert_to_pdf_traditional_success(self):
        self.mock_convert.return_value = None
        
        # Execute
        convert_to_pdf_traditional(os.path.join(self.test_dir, "test"))
        
        # Verify
        self.mock_convert.assert_called_once_with(
            os.path.join(self.test_dir, "test.docx"),
            os.path.join(self.test_dir, "test.pdf")
        )

    def test_convert_to_pdf_traditional_error(self):
        self.mock_convert.side_effect = Exception("Conversion failed")
        
        # Execute and verify
        with self.assertRaises(Exception):
            convert_to_pdf_traditional(os.path.join(self.test_dir, "test"))
        
        # Verify cleanup
        self.mock_convert.assert_called_once()


if __name__ == '__main__':
    unittest.main() 