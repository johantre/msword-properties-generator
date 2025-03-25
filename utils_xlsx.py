from jproperties import Properties
import pandas as pd
import logging
import os


# Fetch properties
try:
    configs = Properties()
    with open('env/prod.properties', 'rb') as read_prop:
        configs.load(read_prop)
except (FileNotFoundError, Exception) as e:
    logging.error(f"❌Error reading properties file: {e}")
    raise SystemExit(e)

# Path constructions
resource_path = configs.get("path.resource").data
xls_offers_log = os.path.join(resource_path, configs.get("base.excel.offers.log").data)
xls_offers_log_sheetname = configs.get("base.excel.offers.log.sheetname").data
xls_offers_provider = os.path.join(resource_path, configs.get("base.excel.offers.provider").data)
xls_offers_provider_sheetname = configs.get("base.excel.offers.provider.sheetname").data
xls_offers_customer = os.path.join(resource_path, configs.get("base.excel.offers.customer").data)
xls_offers_customer_sheetname = configs.get("base.excel.offers.customer.sheetname").data
base_document_name = configs.get("base.word.template").data


def extract_combined_replacements_from_xls(optional_args):
    def merge_replacements(customer_replacements, provider_replacements):
        combined_replacements = {}
        for key, value in provider_replacements.items():
            combined_replacements[f'prov_{key}'] = value
        for key, value in customer_replacements.items():
            combined_replacements[f'cust_{key}'] = value
        return combined_replacements

    provider_replacements = create_sanitized_replacements(xls_offers_provider, xls_offers_provider_sheetname, "prov")
    customer_replacements = create_sanitized_replacements(xls_offers_customer, xls_offers_customer_sheetname, "cust",
                                                          optional_args)
    combined_replacements = merge_replacements(customer_replacements, provider_replacements)
    return combined_replacements


def create_sanitized_replacements(excel_filepath, sheet_name, prefix, optionals=None):
    if optionals :
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
            # Sanitize KEYS ONLY exactly as you require
            sanitized_row_dict = {
                sanitize_spaces_to_variable_name(k): v
                for k, v in row_dict.items()
            }
            sanitized_dict[f'{prefix}_{index}'] = sanitized_row_dict

    return sanitized_dict


def save_to_excel(data_frame, log_data_frame):
    with pd.ExcelWriter(xls_offers_log, mode='w', engine='openpyxl') as log_writer:
        log_data_frame.to_excel(log_writer, sheet_name=xls_offers_log_sheetname, index=False)
    with pd.ExcelWriter(xls_offers_customer, mode='w', engine='openpyxl') as cust_writer:
        data_frame.to_excel(cust_writer, sheet_name=xls_offers_customer_sheetname, index=False)
    return log_data_frame

def safely_read_excel(excel_file, sheet_name, description):
    """
    Intelligent wrapper function clearly handling Excel read and logging errors dynamically.
    """
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

