from unittest.mock import patch
from pathlib import Path
import unittest
import tempfile
import os
import sys


# Add the src directory to the Python path
src_path = str(Path(__file__).resolve().parent.parent / 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from msword_properties_generator.utils.util_config import load_config_values, get_property_value, config

class TestUtilConfig(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.test_properties_path = Path(self.test_dir) / "test.properties"
        
        # Sample properties content
        self.sample_properties = """
path.resource=resources
path.output=output
base.word.template=template
db.file=test.db
path.resource.image_signature_folder=signatures
base.word.namespace.cp=http://schemas.openxmlformats.org/package/2006/metadata/core-properties
base.word.namespace.vt=http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes
base.word.template.image_alt_text_left=Left Image
base.word.template.image_alt_text_right=Right Image
mail.smtp_port=587
mail.smtp_server=smtp.example.com
mail.sender_email=sender@example.com
path.dropbox.destination.folder=/test/dropbox
"""
        
        # Write sample properties to temporary file
        with open(self.test_properties_path, 'w') as f:
            f.write(self.sample_properties)

    def tearDown(self):
        # Clean up temporary files
        if os.path.exists(self.test_properties_path):
            os.remove(self.test_properties_path)
        os.rmdir(self.test_dir)

    @patch('msword_properties_generator.utils.util_config.PROJECT_ROOT', Path('/test/root'))
    def test_load_config_values_success(self):
        """Test successful loading of configuration values"""
        result = load_config_values(self.test_properties_path)
        
        # Test paths configuration
        self.assertIn('paths', result)
        self.assertEqual(result['paths']['resource_path'], 'resources')
        self.assertEqual(result['paths']['output_path'], 'output')
        self.assertEqual(result['paths']['base_document_name'], 'template')
        self.assertEqual(str(result['paths']['db_path']), str(Path('/test/root/resources/test.db')))
        self.assertEqual(str(result['paths']['image_signature_folder']), str(Path('/test/root/resources/signatures')))
        self.assertEqual(str(result['paths']['word_template_path']), str(Path('/test/root/resources/template.docx')))
        self.assertEqual(str(result['paths']['base_output_document_path']), str(Path('/test/root/output/template')))

        # Test namespaces configuration
        self.assertIn('namespaces', result)
        self.assertEqual(result['namespaces']['cp'], 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties')
        self.assertEqual(result['namespaces']['vt'], 'http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes')
        
        # Test alt_texts configuration
        self.assertIn('alt_texts', result)
        self.assertEqual(result['alt_texts']['left'], 'Left Image')
        self.assertEqual(result['alt_texts']['right'], 'Right Image')
        
        # Test mail configuration
        self.assertIn('mail', result)
        self.assertEqual(result['mail']['mail_smtp_port'], '587')
        self.assertEqual(result['mail']['mail_smtp_server'], 'smtp.example.com')
        self.assertEqual(result['mail']['mail_sender_email'], 'sender@example.com')
        
        # Test dropbox configuration
        self.assertIn('dropbox', result)
        self.assertEqual(result['dropbox']['dropbox_destination_folder'], '/test/dropbox')

    def test_load_config_values_file_not_found(self):
        """Test handling of missing properties file"""
        with self.assertRaises(SystemExit):
            load_config_values(Path(self.test_dir) / "nonexistent.properties")

    def test_load_config_values_invalid_properties(self):
        """Test handling of invalid properties file"""
        # Write properties content with one missing critical property
        with open(self.test_properties_path, 'w') as f:
            f.write("""
# Missing path.resource which is critical
path.output=output
base.word.template=template
db.file=test.db
path.resource.image_signature_folder=signatures
base.word.namespace.cp=http://schemas.openxmlformats.org/package/2006/metadata/core-properties
base.word.namespace.vt=http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes
base.word.template.image_alt_text_left=Left Image
base.word.template.image_alt_text_right=Right Image
mail.smtp_port=587
mail.smtp_server=smtp.example.com
mail.sender_email=sender@example.com
path.dropbox.destination.folder=/test/dropbox
""")
        
        with self.assertRaises(SystemExit):
            load_config_values(self.test_properties_path)

    def test_global_config_loaded(self):
        """Test that global config is loaded when module is imported"""
        self.assertIsNotNone(config)
        self.assertIn('paths', config)
        self.assertIn('namespaces', config)
        self.assertIn('mail', config)

if __name__ == '__main__':
    unittest.main() 