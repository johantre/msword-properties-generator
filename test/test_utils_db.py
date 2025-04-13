import os
import sys
import unittest
import sqlite3
from unittest.mock import patch, MagicMock
import base64
import tempfile
import shutil

from msword_properties_generator.data.utils_db import (
    init_db,
    close_db_commit_push,
    commit_db,
    get_inputs_and_encrypt,
    get_leverancier_dict,
    create_table_if_not_exist,
    insert_into_db,
    update_into_db,
    insert_or_update_into_db,
    remove_provider
)

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Import the Git module first to avoid initialization issues
import git

class TestUtilsDB(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for the test database
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, 'test.db')
        
        # Mock the config to use our test database
        self.mock_config = {'paths': {'db_path': self.db_path}}
        self.config_patcher = patch('msword_properties_generator.data.utils_db.config', self.mock_config)
        self.config_patcher.start()
        
        # Import the database functions after mocking config
        from msword_properties_generator.data.utils_db import (
            init_db, close_db_commit_push, get_inputs_and_encrypt,
            insert_into_db, update_into_db, remove_provider,
            get_leverancier_dict
        )
        
        self.db_functions = {
            'init_db': init_db,
            'close_db_commit_push': close_db_commit_push,
            'get_inputs_and_encrypt': get_inputs_and_encrypt,
            'insert_into_db': insert_into_db,
            'update_into_db': update_into_db,
            'remove_provider': remove_provider,
            'get_leverancier_dict': get_leverancier_dict
        }
        
        # Set up encryption and hash mocks
        self.encrypt_patcher = patch('msword_properties_generator.data.utils_db.encrypt')
        self.hash_patcher = patch('msword_properties_generator.data.utils_db.hash')
        self.mock_encrypt = self.encrypt_patcher.start()
        self.mock_hash = self.hash_patcher.start()
        
        # Configure mock return values
        self.mock_encrypt.return_value = 'encrypted_value'
        self.mock_hash.return_value = 'hashed_email'
        
        # Store test environment for modification in tests
        self.test_env = {
            'INPUT_LEVERANCIEREMAIL': 'test@example.com',
            'INPUT_LEVERANCIERNAAM': 'Test Name',
            'INPUT_LEVERANCIERSTAD': 'Test City',
            'INPUT_LEVERANCIERSTRAAT': 'Test Street',
            'INPUT_LEVERANCIERPOSTADRES': 'Test Address',
            'INPUT_LEVERANCIERKANDIDAAT': 'Test Candidate',
            'INPUT_LEVERANCIEROPGEMAAKTTE': 'Test Opgemaaktte',
            'INPUT_LEVERANCIERHOEDANIGHEID': 'Test Hoedanigheid'
        }

    def tearDown(self):
        """Tear down test fixtures."""
        # Stop all patches
        self.config_patcher.stop()
        self.encrypt_patcher.stop()
        self.hash_patcher.stop()
        
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    def test_get_inputs_and_encrypt(self):
        """Test that get_inputs_and_encrypt returns encrypted values."""
        with patch.dict('os.environ', self.test_env):
            encrypted_inputs = self.db_functions['get_inputs_and_encrypt']()
            
            # Verify all fields are encrypted
            self.assertEqual(encrypted_inputs['LeverancierEmail'], 'encrypted_value')
            self.assertEqual(encrypted_inputs['LeverancierNaam'], 'encrypted_value')
            self.assertEqual(encrypted_inputs['LeverancierStad'], 'encrypted_value')
            self.assertEqual(encrypted_inputs['LeverancierStraat'], 'encrypted_value')
            self.assertEqual(encrypted_inputs['LeverancierPostadres'], 'encrypted_value')
            self.assertEqual(encrypted_inputs['LeverancierKandidaat'], 'encrypted_value')
            self.assertEqual(encrypted_inputs['LeverancierOpgemaaktte'], 'encrypted_value')
            self.assertEqual(encrypted_inputs['LeverancierHoedanigheid'], 'encrypted_value')
            
            # Verify encrypt was called 8 times (once for each field)
            self.assertEqual(self.mock_encrypt.call_count, 8)

    def test_invalid_email(self):
        """Test that invalid email raises ValueError."""
        test_env = self.test_env.copy()
        test_env['INPUT_LEVERANCIEREMAIL'] = 'invalid_email'
        
        with patch.dict('os.environ', test_env):
            with self.assertRaises(ValueError):
                self.db_functions['get_inputs_and_encrypt']()

    def test_insert_and_get_provider(self):
        """Test inserting and retrieving a provider."""
        with patch.dict('os.environ', self.test_env):
            # Mock the database connection and cursor
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            
            # Get encrypted inputs
            encrypted_inputs = self.db_functions['get_inputs_and_encrypt']()
            
            # Insert provider
            self.db_functions['insert_into_db'](mock_conn, 'test@example.com', encrypted_inputs)
            
            # Verify insert was called with correct parameters
            mock_cursor.execute.assert_called_with(
                '''
        INSERT INTO offer_providers (
            HashedLeverancierEmail, 
            LeverancierEmail, 
            LeverancierNaam, 
            LeverancierStad, 
            LeverancierStraat, 
            LeverancierPostadres, 
            LeverancierKandidaat, 
            LeverancierOpgemaaktte, 
            LeverancierHoedanigheid
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''',
                ('hashed_email', 'encrypted_value', 'encrypted_value', 'encrypted_value',
                 'encrypted_value', 'encrypted_value', 'encrypted_value', 'encrypted_value',
                 'encrypted_value')
            )

    def test_update_provider(self):
        """Test updating a provider."""
        with patch.dict('os.environ', self.test_env):
            # Mock the database connection and cursor
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            
            # Get encrypted inputs
            encrypted_inputs = self.db_functions['get_inputs_and_encrypt']()
            
            # Update provider
            success = self.db_functions['update_into_db'](mock_conn, 'test@example.com', encrypted_inputs)
            
            # Verify update was called with correct parameters
            expected_fields = ", ".join([f"{key} = ?" for key in encrypted_inputs.keys()])
            expected_params = ['encrypted_value'] * len(encrypted_inputs) + ['hashed_email']
            
            mock_cursor.execute.assert_called_with(
                f"""
        UPDATE offer_providers 
        SET {expected_fields}
        WHERE HashedLeverancierEmail = ?
    """,
                expected_params
            )

    def test_remove_provider(self):
        """Test removing a provider."""
        with patch.dict('os.environ', self.test_env):
            # Mock the database connection and cursor
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            
            # Mock check_leverancier_count to return 1 (provider exists)
            with patch('msword_properties_generator.data.utils_db.check_leverancier_count', return_value=1):
                # Remove provider
                success = self.db_functions['remove_provider'](mock_conn)
                self.assertTrue(success)
                
                # Verify delete was called with correct parameters
                mock_cursor.execute.assert_called_with(
                    "DELETE FROM offer_providers WHERE HashedLeverancierEmail = ?",
                    ('hashed_email',)
                )

    def test_close_db_commit_push(self):
        """Test closing the database and pushing changes."""
        with patch.dict('os.environ', self.test_env):
            # Mock the database connection
            mock_conn = MagicMock()
            
            # Mock git functions
            with patch('msword_properties_generator.data.utils_db.git_stage_commit_push') as mock_git_push:
                with patch('msword_properties_generator.data.utils_db.get_repo_root', return_value='/mock/repo/root'):
                    # Close database and push changes
                    self.db_functions['close_db_commit_push'](mock_conn)
                    
                    # Verify database was closed
                    mock_conn.close.assert_called_once()
                    
                    # Verify git push was called
                    mock_git_push.assert_called_once()

    def test_get_leverancier_dict(self):
        """Test getting leverancier dictionary."""
        with patch.dict('os.environ', self.test_env):
            # Mock the database connection and cursor
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            
            # Mock the decrypt function
            with patch('msword_properties_generator.data.utils_db.decrypt',
                      return_value='decrypted_value') as mock_decrypt:
                # Mock cursor.fetchall to return a row
                mock_cursor.fetchall.return_value = [(
                    1,  # id
                    'hashed_email',  # HashedLeverancierEmail
                    'encrypted_value',  # LeverancierEmail
                    'encrypted_value',  # LeverancierNaam
                    'encrypted_value',  # LeverancierStad
                    'encrypted_value',  # LeverancierStraat
                    'encrypted_value',  # LeverancierPostadres
                    'encrypted_value',  # LeverancierKandidaat
                    'encrypted_value',  # LeverancierOpgemaaktte
                    'encrypted_value'   # LeverancierHoedanigheid
                )]
                
                # Mock get_column_names to return the column names
                with patch('msword_properties_generator.data.utils_db.get_column_names',
                          return_value=[
                              'LeverancierEmail',
                              'LeverancierNaam',
                              'LeverancierStad',
                              'LeverancierStraat',
                              'LeverancierPostadres',
                              'LeverancierKandidaat',
                              'LeverancierOpgemaaktte',
                              'LeverancierHoedanigheid'
                          ]) as mock_get_columns:
                    
                    # Get leverancier dict
                    result = self.db_functions['get_leverancier_dict'](mock_conn, 'test@example.com')
                    
                    # Verify the result
                    self.assertIn('prov_0', result)
                    provider = result['prov_0']
                    self.assertEqual(provider['LeverancierEmail'], 'decrypted_value')
                    self.assertEqual(provider['LeverancierNaam'], 'decrypted_value')
                    self.assertEqual(provider['LeverancierStad'], 'decrypted_value')
                    self.assertEqual(provider['LeverancierStraat'], 'decrypted_value')
                    self.assertEqual(provider['LeverancierPostadres'], 'decrypted_value')
                    self.assertEqual(provider['LeverancierKandidaat'], 'decrypted_value')
                    self.assertEqual(provider['LeverancierOpgemaaktte'], 'decrypted_value')
                    self.assertEqual(provider['LeverancierHoedanigheid'], 'decrypted_value')
                    
                    # Verify the SQL query
                    mock_cursor.execute.assert_called_with(
                        "SELECT * FROM offer_providers where HashedLeverancierEmail = ?",
                        ('hashed_email',)
                    )

if __name__ == '__main__':
    unittest.main() 