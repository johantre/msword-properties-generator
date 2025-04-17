from msword_properties_generator.main.subscribe_or_update_provider import main
from unittest.mock import patch, MagicMock
import unittest


class TestSubscribeOrUpdateProvider(unittest.TestCase):

    @patch('msword_properties_generator.main.subscribe_or_update_provider.close_db_commit_push')
    @patch('msword_properties_generator.main.subscribe_or_update_provider.commit_db')
    @patch('msword_properties_generator.main.subscribe_or_update_provider.insert_or_update_into_db')
    @patch('msword_properties_generator.main.subscribe_or_update_provider.get_image_and_encrypt_to_image_folder')
    @patch('msword_properties_generator.main.subscribe_or_update_provider.get_inputs_and_encrypt')
    @patch('msword_properties_generator.main.subscribe_or_update_provider.create_table_if_not_exist')
    @patch('msword_properties_generator.main.subscribe_or_update_provider.init_db')
    @patch('msword_properties_generator.main.subscribe_or_update_provider.setup_logging')
    def test_main_happy_path(self,
                             mock_setup_logging,
                             mock_init_db,
                             mock_create_table,
                             mock_get_inputs_encrypt,
                             mock_image_encrypt,
                             mock_insert_or_update,
                             mock_commit_db,
                             mock_close_db):
        mock_conn = MagicMock()
        mock_init_db.return_value = mock_conn
        mock_get_inputs_encrypt.return_value = {'encrypted_email': 'dummy_encrypted_data'}

        main()

        mock_setup_logging.assert_called_once()
        mock_init_db.assert_called_once()
        mock_create_table.assert_called_once_with(mock_conn)
        mock_get_inputs_encrypt.assert_called_once()
        mock_image_encrypt.assert_called_once()
        mock_insert_or_update.assert_called_once_with(mock_conn, {'encrypted_email': 'dummy_encrypted_data'})
        mock_commit_db.assert_called_once_with(mock_conn)
        mock_close_db.assert_called_once_with(mock_conn)

    @patch('msword_properties_generator.main.subscribe_or_update_provider.close_db_commit_push')
    @patch('msword_properties_generator.main.subscribe_or_update_provider.commit_db')
    @patch('msword_properties_generator.main.subscribe_or_update_provider.insert_or_update_into_db')
    @patch('msword_properties_generator.main.subscribe_or_update_provider.get_image_and_encrypt_to_image_folder')
    @patch('msword_properties_generator.main.subscribe_or_update_provider.get_inputs_and_encrypt')
    @patch('msword_properties_generator.main.subscribe_or_update_provider.create_table_if_not_exist')
    @patch('msword_properties_generator.main.subscribe_or_update_provider.init_db')
    @patch('msword_properties_generator.main.subscribe_or_update_provider.setup_logging')
    @patch('logging.error')
    def test_main_invalid_email(
            self,
            mock_logging_error,
            mock_setup_logging,
            mock_init_db,
            mock_create_table,
            mock_get_inputs_encrypt,
            mock_image_encrypt,
            mock_insert_or_update,
            mock_commit_db,
            mock_close_db):
        mock_conn = MagicMock()
        mock_init_db.return_value = mock_conn
        mock_get_inputs_encrypt.side_effect = ValueError("Invalid email address: None")

        with self.assertRaises(ValueError):
            main()

        mock_logging_error.assert_called_once_with("🛑 An error occurred, exiting.")
        mock_commit_db.assert_not_called()
        mock_close_db.assert_called_once_with(mock_conn)


if __name__ == '__main__':
    unittest.main()
