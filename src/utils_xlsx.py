from util_config import config  # importing centralized config
import pandas as pd
import logging


def save_to_excel(data_frame, log_data_frame):
    with pd.ExcelWriter(config["paths"]["xls_offers_log"], mode='w', engine='openpyxl') as log_writer:
        log_data_frame.to_excel(log_writer, sheet_name=config["paths"]["xls_offers_log_sheetname"], index=False)
    with pd.ExcelWriter(config["paths"]["xls_offers_customer"], mode='w', engine='openpyxl') as cust_writer:
        data_frame.to_excel(cust_writer, sheet_name=config["paths"]["xls_offers_customer_sheetname"], index=False)
    return log_data_frame

def safely_read_excel(excel_file, sheet_name, description):
    try:
        return pd.read_excel(excel_file, sheet_name)
    except ValueError as e:
        error_msg = f"❌ValueError occurred reading {description} Excel file '{excel_file}', sheet '{sheet_name}': {e}"
        logging.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"❌Unexpected error reading {description} Excel file '{excel_file}', sheet '{sheet_name}': {e}"
        logging.error(error_msg)
        raise

def sanitize_spaces_to_variable_name(any_string):
    return any_string.replace(" ", "")

def create_replacements_from_xls(excel_filepath, sheet_name, optionals=None):
    prefix = 'cust'

    if optionals:
        sanitized_dict = {}
        sanitized_row_dict = {
            sanitize_spaces_to_variable_name(k): v
            for k, v in optionals.items()
        }
        sanitized_dict[f'{prefix}_0'] = sanitized_row_dict
        return sanitized_dict

    df = pd.read_excel(excel_filepath, sheet_name=sheet_name, header=0)
    if df.empty:
        logging.warning(f"⚠️The provided Excel file '{excel_filepath}' with sheet '{sheet_name}' is empty, No data to process. Please verify the contents.")
        sanitized_dict = {
            sanitize_spaces_to_variable_name(column_name): 'prov_0'
            for column_name in df.columns
        }
    else:
        sanitized_dict = {}
        for index, row in df.iterrows():
            row_dict = row.to_dict()
            sanitized_row_dict = {
                sanitize_spaces_to_variable_name(k): v
                for k, v in row_dict.items()
            }
            sanitized_dict[f'{prefix}_{index}'] = sanitized_row_dict

    return sanitized_dict
