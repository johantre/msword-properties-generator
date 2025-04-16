import unittest
from unittest.mock import patch
from msword_properties_generator.main.generate_offer_documents import extract_combined_replacements, _main, create_replacements_from_args


class TestGenerateOfferDocuments(unittest.TestCase):

    def test_create_replacements_from_valid_args(self):
        main_args = {'klantJobReference': 'BMW-WP-001',
            'klantJobTitle': 'Worstenprikker',
            'klantNaam': 'Brood Met Worst'}

        expected_result = {'cust_0': {'klantJobReference': 'BMW-WP-001',
            'klantJobTitle': 'Worstenprikker',
            'klantNaam': 'Brood Met Worst'}}

        result = create_replacements_from_args(main_args)
        self.assertEqual(result, expected_result)

    def test_create_replacements_with_missing_keys(self):
        # Only 1 key provided
        main_args = {
            "klantNaam": "SmoskeCo"
        }

        expected_result = {'cust_0': {
            "klantNaam": "SmoskeCo"
        }}

        result = create_replacements_from_args(main_args)
        self.assertEqual(result, expected_result)

    def test_create_replacements_with_empty_args(self):
        result = create_replacements_from_args({})
        self.assertEqual(result, {'cust_0': {}})

    def test_create_replacements_with_none(self):
        result = create_replacements_from_args(None)
        self.assertEqual(result, {'cust_0': {}})

    @patch('msword_properties_generator.main.generate_offer_documents.dropbox_upload')
    @patch('msword_properties_generator.main.generate_offer_documents.send_email')
    @patch('msword_properties_generator.main.generate_offer_documents.convert_to_pdf')
    @patch('msword_properties_generator.main.generate_offer_documents.update_custom_properties_docx_structure')
    @patch('msword_properties_generator.main.generate_offer_documents.extract_combined_replacements')
    def test_main_flow_with_upload_and_email(
        self,
        mock_extract_combined_replacements,
        mock_update,
        mock_convert,
        mock_send,
        mock_dropbox
    ):
        # Setup: simulate one provider + one customer
        mock_extract_combined_replacements.return_value = {
            'prov_key': {'Naam': 'ProviderCo'},
            'cust_key': {'KlantNaam': 'KlantX'}
        }

        mock_update.return_value = "test/path/output_doc"

        main_args = {
            "LeverancierEmail": "test@example.com",
            "UploadDropbox": "true"
        }

        # Act
        _main(verbose=True, main_args=main_args)

        # Assert
        mock_send.assert_called_once()
        mock_dropbox.assert_called_once()
        mock_convert.assert_called_once()
        mock_update.assert_called_once()

    @patch('msword_properties_generator.main.generate_offer_documents.dropbox_upload')
    @patch('msword_properties_generator.main.generate_offer_documents.send_email')
    @patch('msword_properties_generator.main.generate_offer_documents.convert_to_pdf')
    @patch('msword_properties_generator.main.generate_offer_documents.update_custom_properties_docx_structure')
    @patch('msword_properties_generator.main.generate_offer_documents.extract_combined_replacements')
    def test_main_flow_without_upload(
        self,
        mock_extract_combined_replacements,
        mock_update,
        mock_convert,
        mock_send,
        mock_dropbox
    ):
        # Setup: simulate one provider + one customer
        mock_extract_combined_replacements.return_value = {
            'prov_key': {'Naam': 'ProviderCo'},
            'cust_key': {'KlantNaam': 'KlantX'}
        }

        mock_update.return_value = "test/path/output_doc"

        main_args = {
            "LeverancierEmail": "test@example.com",
            "UploadDropbox": "false"
        }

        # Act
        _main(verbose=False, main_args=main_args)

        # Assert
        mock_send.assert_called_once()
        mock_dropbox.assert_not_called()

    @patch('msword_properties_generator.main.generate_offer_documents.create_replacements_from_db')
    def test_extract_combined_replacements_with_mocked_db(
            self,
            mock_create_replacements_from_db,
    ):
        # Arrange - Mock responses
        mock_create_replacements_from_db.return_value = {
            'db_key1': 'db_value1', 'db_key2': 'db_value2'
        }

        optional_args = {"LeverancierEmail": "test@example.com"}
        expected_output = {'cust_cust_0': {'LeverancierEmail': 'test@example.com'},
            'prov_db_key1': 'db_value1',
            'prov_db_key2': 'db_value2'
        }

        # Act
        result = extract_combined_replacements(optional_args)

        # Assert
        self.assertEqual(result, expected_output)
        mock_create_replacements_from_db.assert_called_once_with(optional_args)

    def test_extract_combined_replacements_missing_leverancier_email(self):
        optional_args = {"IncorrectEmailKey": "test@example.com"}

        with self.assertRaises(ValueError) as context:
            extract_combined_replacements(optional_args)

        expected_message = ("LeverancierEmail ontbreekt in 'optional_args'. "
                            "Zorg ervoor dat dit veld correct wordt meegegeven.")
        self.assertEqual(str(context.exception), expected_message)


if __name__ == '__main__':
    unittest.main()
