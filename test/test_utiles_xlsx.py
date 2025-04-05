import unittest
from unittest.mock import patch, MagicMock
from utils_xlsx import save_to_excel, safely_read_excel, sanitize_spaces_to_variable_name, create_replacements_from_xls
import pandas as pd


class TestUtilsXlsx(unittest.TestCase):

    @patch('utils_xlsx.pd.ExcelWriter')  # Mock ExcelWriter from Pandas
    @patch('utils_xlsx.config')  # Mock config import
    def test_save_to_excel(self, mock_config, mock_excel_writer):
        # Arrange
        mock_config.__getitem__.side_effect = lambda key: {
            "paths": {
                "xls_offers_customer": "test_file.xlsx",
                "xls_offers_customer_sheetname": "Customer"
            }
        }[key]

        mock_writer_instance = mock_excel_writer.return_value.__enter__.return_value
        sample_df = pd.DataFrame({"Column": [1, 2, 3]})
        log_df = pd.DataFrame({"LogColumn": ['Log1', 'Log2']})

        # Act
        returned_log_df = save_to_excel(sample_df, log_df)

        # Assert
        mock_excel_writer.assert_called_once_with("test_file.xlsx", mode='w', engine='openpyxl')
        sample_df.to_excel.assert_not_called()  # original to_excel from pandas is not mocked, should not directly assert it here.
        mock_writer_instance.__enter__.assert_not_called()
        self.assertTrue(returned_log_df.equals(log_df))

    @patch('utils_xlsx.pd.read_excel')
    def test_safely_read_excel_success(self, mock_read_excel):
        # Arrange
        expected_df = pd.DataFrame({"A": [1, 2, 3]})
        mock_read_excel.return_value = expected_df

        # Act
        df = safely_read_excel("dummy.xlsx", "Sheet1", "test_description")

        # Assert
        mock_read_excel.assert_called_once_with("dummy.xlsx", "Sheet1")
        self.assertTrue(df.equals(expected_df))

    @patch('utils_xlsx.pd.read_excel')
    def test_safely_read_excel_failure(self, mock_read_excel):
        # Arrange
        mock_read_excel.side_effect = ValueError("Sheet not found")

        # Act and Assert
        with self.assertRaises(ValueError):
            safely_read_excel("dummy.xlsx", "InvalidSheet", "test_description")

        mock_read_excel.assert_called_once_with("dummy.xlsx", "InvalidSheet")

    def test_sanitize_spaces_to_variable_name(self):
        # Arrange & Act & Assert
        self.assertEqual(sanitize_spaces_to_variable_name("Column One"), "ColumnOne")
        self.assertEqual(sanitize_spaces_to_variable_name(" Another Col "), "AnotherCol")
        self.assertEqual(sanitize_spaces_to_variable_name("NoSpaces"), "NoSpaces")

    @patch('utils_xlsx.pd.read_excel')
    def test_create_replacements_from_xls_with_optionals(self, mock_read_excel):
        # Arrange
        optional_data = {"Column One": "Value 1", "Column Two": "Value 2"}

        # Act
        sanitized_dict = create_replacements_from_xls("dummy.xlsx", "SheetName", optionals=optional_data)

        # Assert
        mock_read_excel.assert_not_called()  # Should not read from excel if optionals provided
        expected_result = {
            "cust_0": {
                "ColumnOne": "Value 1",
                "ColumnTwo": "Value 2"
            }
        }
        self.assertEqual(sanitized_dict, expected_result)

    @patch('utils_xlsx.pd.read_excel')
    def test_create_replacements_from_xls_empty_dataframe(self, mock_read_excel):
        # Arrange
        mock_df = pd.DataFrame(columns=["Column One", "Column Two"])
        mock_read_excel.return_value = mock_df

        # Act
        sanitized_dict = create_replacements_from_xls("dummy.xlsx", "SheetName")

        # Assert
        expected_result = {
            "ColumnOne": "prov_0",
            "ColumnTwo": "prov_0"
        }
        self.assertEqual(sanitized_dict, expected_result)

    @patch('utils_xlsx.pd.read_excel')
    def test_create_replacements_from_xls_nonempty_dataframe(self, mock_read_excel):
        # Arrange
        mock_df = pd.DataFrame({
            "Column One": ["Value 1", "Value 2"],
            "Column Two": ["Value 3", "Value 4"]
        })
        mock_read_excel.return_value = mock_df

        # Act
        sanitized_dict = create_replacements_from_xls("dummy.xlsx", "SheetName")

        # Assert
        expected_result = {
            'cust_0': {'ColumnOne': 'Value 1', 'ColumnTwo': 'Value 3'},
            'cust_1': {'ColumnOne': 'Value 2', 'ColumnTwo': 'Value 4'}
        }
        self.assertEqual(sanitized_dict, expected_result)


if __name__ == '__main__':
    unittest.main()
