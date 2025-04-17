from unittest.mock import patch, MagicMock
import unittest
import tempfile
import sqlite3
import shutil
import os
import sys


# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

class TestUtilsDB(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for the test database
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, 'test.db')
        
        # Mock the config to use our test database
        self.mock_config = {'paths': {'db_path': self.db_path}}
        self.config_patcher = patch('msword_properties_generator.data.utils_db.config', self.mock_config)
        self.config_patcher.start()
        
        # Import the database functions after mocking config
        from msword_properties_generator.data.utils_db import (
            init_db, commit_db, close_db_commit_push, get_inputs_and_encrypt,
            insert_into_db, update_into_db, remove_provider,
            get_leverancier_dict,
            create_table_if_not_exist,
            insert_or_update_into_db,
            create_replacements_from_db,
            get_column_names,
            check_leverancier_count
        )
        
        self.db_functions = {
            'init_db': init_db,
            'commit_db': commit_db,
            'close_db_commit_push': close_db_commit_push,
            'get_inputs_and_encrypt': get_inputs_and_encrypt,
            'insert_into_db': insert_into_db,
            'update_into_db': update_into_db,
            'remove_provider': remove_provider,
            'get_leverancier_dict': get_leverancier_dict,
            'create_table_if_not_exist': create_table_if_not_exist,
            'get_column_names': get_column_names,
            'check_leverancier_count': check_leverancier_count,
            'insert_or_update_into_db': insert_or_update_into_db,
            'create_replacements_from_db': create_replacements_from_db
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
        # Stop all patches
        self.config_patcher.stop()
        self.encrypt_patcher.stop()
        self.hash_patcher.stop()
        
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    def test_get_inputs_and_encrypt(self):
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
        test_env = self.test_env.copy()
        test_env['INPUT_LEVERANCIEREMAIL'] = 'invalid_email'
        
        with patch.dict('os.environ', test_env):
            with self.assertRaises(ValueError):
                self.db_functions['get_inputs_and_encrypt']()

    def test_insert_and_get_provider(self):
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
            mock_conn.close()

    def test_update_provider(self):
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
            mock_conn.close()

    def test_remove_provider(self):
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
            mock_conn.close()

    def test_close_db_commit_push(self):
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
            mock_conn.close()

    def test_get_leverancier_dict(self):
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
            mock_conn.close()

    def test_create_table(self):
        mock_conn = sqlite3.connect(':memory:')
        self.db_functions['create_table_if_not_exist'](mock_conn)
        cursor = mock_conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='offer_providers'")
        assert cursor.fetchone() is not None
        mock_conn.close()

    def test_commit_db_with_mock(self):
        mock_conn = MagicMock()
        self.db_functions['commit_db'](mock_conn)
        mock_conn.commit.assert_called_once()
        mock_conn.close()

    def test_get_column_names(self):
        mock_conn = sqlite3.connect(":memory:")
        self.db_functions['create_table_if_not_exist'](mock_conn)
        expected_columns = [
            "LeverancierEmail",
            "LeverancierNaam",
            "LeverancierStad",
            "LeverancierStraat",
            "LeverancierPostadres",
            "LeverancierKandidaat",
            "LeverancierOpgemaaktte",
            "LeverancierHoedanigheid"
        ]
        assert self.db_functions['get_column_names'](mock_conn, "offer_providers") == expected_columns
        mock_conn.close()

    def test_get_column_names_table_does_not_exist(self):
        mock_conn = sqlite3.connect(":memory:")
        with self.assertRaises(sqlite3.OperationalError):
            self.db_functions['get_column_names'](mock_conn, "non_existing_table")
        mock_conn.close()

    def test_check_leverancier_count_none(self):
        mock_conn = sqlite3.connect(":memory:")
        self.db_functions['create_table_if_not_exist'](mock_conn)

        count = self.db_functions['check_leverancier_count'](mock_conn, "nonexistent@example.com")
        self.assertEqual(count, 0)
        mock_conn.close()

    def test_check_leverancier_count_one(self):
        mock_conn = sqlite3.connect(":memory:")
        self.db_functions['create_table_if_not_exist'](mock_conn)

        email = "test@example.com"
        test_data = {
            "HashedLeverancierEmail": str(hash(email)),
            "LeverancierEmail": email,
            "LeverancierNaam": "Test Leverancier",
            "LeverancierStad": "Gent",
            "LeverancierStraat": "Teststraat 1",
            "LeverancierPostadres": "9000",
            "LeverancierKandidaat": "Jan Jansen",
            "LeverancierOpgemaaktte": "2025-04-16",
            "LeverancierHoedanigheid": "Manager"
        }
        encrypted_inputs = {
            'LeverancierEmail': email,
            'LeverancierNaam': "Test Leverancier",
            'LeverancierStad': "Gent",
            'LeverancierStraat': "Teststraat 1",
            'LeverancierPostadres': "9000",
            'LeverancierKandidaat': "Jan Jansen",
            'LeverancierOpgemaaktte': "2025-04-16",
            'LeverancierHoedanigheid': "Manager"
        }
        self.db_functions['insert_into_db'](mock_conn, test_data, encrypted_inputs)

        count = self.db_functions['check_leverancier_count'](mock_conn, email)
        self.assertEqual(count, 1)
        mock_conn.close()

    def test_insert_or_update_into_db_insert_new(self):
        os.environ.update(self.test_env)

        mock_conn = sqlite3.connect(":memory:")
        self.db_functions['create_table_if_not_exist'](mock_conn)

        encrypted_inputs = {
            'LeverancierEmail': 'encrypted_value',
            'LeverancierNaam': 'encrypted_value',
            'LeverancierStad': 'encrypted_value',
            'LeverancierStraat': 'encrypted_value',
            'LeverancierPostadres': 'encrypted_value',
            'LeverancierKandidaat': 'encrypted_value',
            'LeverancierOpgemaaktte': 'encrypted_value',
            'LeverancierHoedanigheid': 'encrypted_value'
        }

        self.db_functions['insert_or_update_into_db'](mock_conn, encrypted_inputs)

        cursor = mock_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM offer_providers")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 1)
        mock_conn.close()

    def test_insert_or_update_into_db_update_existing(self):
        os.environ.update(self.test_env)

        mock_conn = sqlite3.connect(":memory:")
        self.db_functions['create_table_if_not_exist'](mock_conn)

        leverancier_email = self.test_env['INPUT_LEVERANCIEREMAIL']
        encrypted_inputs_initial = {
            key: 'initial_value' for key in [
                'LeverancierEmail', 'LeverancierNaam', 'LeverancierStad',
                'LeverancierStraat', 'LeverancierPostadres',
                'LeverancierKandidaat', 'LeverancierOpgemaaktte',
                'LeverancierHoedanigheid'
            ]
        }

        self.db_functions['insert_into_db'](mock_conn, leverancier_email, encrypted_inputs_initial)

        encrypted_inputs_updated = {
            key: 'updated_value' for key in encrypted_inputs_initial
        }

        self.db_functions['insert_or_update_into_db'](mock_conn, encrypted_inputs_updated)

        cursor = mock_conn.cursor()
        cursor.execute("SELECT * FROM offer_providers")
        row = cursor.fetchone()

        self.assertEqual(row[2], 'updated_value')  # LeverancierEmail
        mock_conn.close()

    def mock_decrypt(value):
        return value

    @patch('msword_properties_generator.data.utils_db.decrypt', side_effect=mock_decrypt)
    @patch('msword_properties_generator.utils.utils_hash_encrypt.get_encryption_key')
    @patch('msword_properties_generator.data.utils_db.init_db')
    def test_create_replacements_from_db(self, mock_init_db, mock_get_encryption_key, mock_decrypt):
        from cryptography.fernet import Fernet
        valid_key = Fernet.generate_key()
        mock_get_encryption_key.return_value = valid_key
        mock_init_db.return_value = sqlite3.connect(":memory:")

        # Setup environment variables
        os.environ.update(self.test_env)

        mock_conn = mock_init_db.return_value
        cursor = mock_conn.cursor()
        cursor.execute('''
            CREATE TABLE offer_providers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                HashedLeverancierEmail TEXT,
                LeverancierEmail TEXT,
                LeverancierNaam TEXT,
                LeverancierStad TEXT,
                LeverancierStraat TEXT,
                LeverancierPostadres TEXT,
                LeverancierKandidaat TEXT,
                LeverancierOpgemaaktte TEXT,
                LeverancierHoedanigheid TEXT
            )
        ''')
        mock_conn.commit()

        # Vul de table met testdata
        cursor.execute('''
            INSERT INTO offer_providers (
                HashedLeverancierEmail, LeverancierEmail, LeverancierNaam, LeverancierStad,
                LeverancierStraat, LeverancierPostadres, LeverancierKandidaat, LeverancierOpgemaaktte,
                LeverancierHoedanigheid
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'hashed_email', 'test@example.com', 'Test Name', 'Test City', 'Test Street',
            'Test Address', 'Test Candidate', 'Test Opgemaaktte', 'Test Hoedanigheid'
        ))
        mock_conn.commit()

        optionals = {'LeverancierEmail': 'test@example.com'}
        replacements = self.db_functions['create_replacements_from_db'](optionals)

        self.assertIn('LeverancierEmail', replacements['prov_0'])
        self.assertEqual(replacements['prov_0']['LeverancierEmail'], 'test@example.com')
        mock_conn.close()

if __name__ == '__main__':
    unittest.main() 