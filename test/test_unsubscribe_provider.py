from msword_properties_generator.main.unsubscribe_provider import main
from unittest.mock import patch, MagicMock
import unittest


class TestUnsubscribeProvider(unittest.TestCase):

    @patch('msword_properties_generator.main.unsubscribe_provider.close_db_commit_push')
    @patch('msword_properties_generator.main.unsubscribe_provider.commit_db')
    @patch('msword_properties_generator.main.unsubscribe_provider.remove_from_image_folder_git_commit_push')
    @patch('msword_properties_generator.main.unsubscribe_provider.remove_provider')
    @patch('msword_properties_generator.main.unsubscribe_provider.init_db')
    @patch('msword_properties_generator.main.unsubscribe_provider.setup_logging')
    def test_main_remove_successful(self,
                                    mock_setup_logging,
                                    mock_init_db,
                                    mock_remove_provider,
                                    mock_remove_image_commit_push,
                                    mock_commit_db,
                                    mock_close_db):
        # Arrange
        mock_conn = MagicMock()
        mock_init_db.return_value = mock_conn
        mock_remove_provider.return_value = True

        # Act
        main()

        # Assert
        mock_setup_logging.assert_called_once()
        mock_init_db.assert_called_once()

        mock_remove_provider.assert_called_once_with(mock_conn)
        mock_remove_image_commit_push.assert_called_once()

        mock_commit_db.assert_called_once_with(mock_conn)
        mock_close_db.assert_called_once_with(mock_conn)

    @patch('msword_properties_generator.main.unsubscribe_provider.close_db_commit_push')
    @patch('msword_properties_generator.main.unsubscribe_provider.commit_db')
    @patch('msword_properties_generator.main.unsubscribe_provider.remove_from_image_folder_git_commit_push')
    @patch('msword_properties_generator.main.unsubscribe_provider.remove_provider')
    @patch('msword_properties_generator.main.unsubscribe_provider.init_db')
    @patch('msword_properties_generator.main.unsubscribe_provider.setup_logging')
    def test_main_remove_unsuccessful(self,
                                      mock_setup_logging,
                                      mock_init_db,
                                      mock_remove_provider,
                                      mock_remove_image_commit_push,
                                      mock_commit_db,
                                      mock_close_db):
        # Arrange
        mock_conn = MagicMock()
        mock_init_db.return_value = mock_conn
        mock_remove_provider.return_value = False

        # Act
        main()

        # Assert
        mock_setup_logging.assert_called_once()
        mock_init_db.assert_called_once()

        mock_remove_provider.assert_called_once_with(mock_conn)
        mock_remove_image_commit_push.assert_not_called()

        mock_commit_db.assert_called_once_with(mock_conn)
        mock_close_db.assert_called_once_with(mock_conn)


if __name__ == '__main__':
    unittest.main()
