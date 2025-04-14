import unittest
from unittest.mock import patch
from msword_properties_generator.main.generate_offer_documents import extract_combined_replacements


class TestGenerateOfferDocuments(unittest.TestCase):

    @patch('msword_properties_generator.main.generate_offer_documents.config', new={
        "paths": {
            "xls_offers_customer": "mock/path/to/file.xlsx",
            "xls_offers_customer_sheetname": "MockSheetName"
        }
    })
    @patch('msword_properties_generator.main.generate_offer_documents.create_replacements_from_xls')
    @patch('msword_properties_generator.main.generate_offer_documents.create_replacements_from_db')
    def test_extract_combined_replacements_with_mocked_db_and_xls(
            self,
            mock_create_replacements_from_db,
            mock_create_replacements_from_xls
    ):
        # Arrange - Mock responses
        mock_create_replacements_from_db.return_value = {
            'db_key1': 'db_value1', 'db_key2': 'db_value2'
        }
        mock_create_replacements_from_xls.return_value = {
            'xls_key1': 'xls_value1', 'xls_key2': 'xls_value2'
        }

        optional_args = {"LeverancierEmail": "test@example.com"}
        expected_output = {
            'prov_db_key1': 'db_value1',
            'prov_db_key2': 'db_value2',
            'cust_xls_key1': 'xls_value1',
            'cust_xls_key2': 'xls_value2'
        }

        # Act
        result = extract_combined_replacements(optional_args)

        # Assert
        self.assertEqual(result, expected_output)
        mock_create_replacements_from_db.assert_called_once_with(optional_args)
        mock_create_replacements_from_xls.assert_called_once_with(
            "mock/path/to/file.xlsx",
            "MockSheetName",
            optional_args
        )

    def test_extract_combined_replacements_missing_leverancier_email(self):
        optional_args = {"IncorrectEmailKey": "test@example.com"}

        with self.assertRaises(ValueError) as context:
            extract_combined_replacements(optional_args)

        expected_message = ("LeverancierEmail ontbreekt in 'optional_args'. "
                            "Zorg ervoor dat dit veld correct wordt meegegeven.")
        self.assertEqual(str(context.exception), expected_message)


if __name__ == '__main__':
    unittest.main()
