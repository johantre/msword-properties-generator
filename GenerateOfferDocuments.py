from docxcompose.properties import CustomProperties
from jproperties import Properties
from docx2pdf import convert
from docx import Document
import pandas as pd
import logging
import re
import os

#logging
logging.basicConfig(level=logging.INFO, filename='offer_generation.log', format='%(asctime)s %(levelname)s %(message)s')

# Fetch properties
configs = Properties()
with open('env/prod.properties', 'rb') as read_prop:
    configs.load(read_prop)

# Path constructions
resource_path = configs.get("path.resource").data
output_path = configs.get("path.output").data
xls_offers_log = resource_path + configs.get("base.excel.offers.log").data
xls_offers_log_sheetname = configs.get("base.excel.offers.log.sheetname").data
xls_offers_provider = resource_path + configs.get("base.excel.offers.provider").data
xls_offers_provider_sheetname = configs.get("base.excel.offers.provider.sheetname").data
xls_offers_customer = resource_path + configs.get("base.excel.offers.customer").data
xls_offers_customer_sheetname = configs.get("base.excel.offers.customer.sheetname").data
base_document_name = configs.get("base.word.template").data
word_template_path = resource_path + base_document_name + '.docx'
base_output_document_path = output_path + base_document_name


def _main():
    # Read the Excel files into a DataFrames
    try:
        log_data_frame = pd.read_excel(xls_offers_log, xls_offers_log_sheetname)
    except ValueError as e:
        logging.error(f"Error reading offers log Excel file {xls_offers_log}: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error reading Excel file '{xls_offers_log}': {e}")
        raise

    try:
        new_data_frame_provider = pd.read_excel(xls_offers_provider, xls_offers_provider_sheetname)
    except ValueError as e:
        logging.error(f"Error reading offers provider Excel file {xls_offers_provider}: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error reading Excel file '{xls_offers_provider}': {e}")
        raise
    try:
        new_data_frame_customer = pd.read_excel(xls_offers_customer, xls_offers_customer_sheetname)
    except ValueError as e:
        logging.error(f"Error reading offers customer Excel file {xls_offers_customer}: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error reading Excel file '{xls_offers_customer}': {e}")
        raise

    # Each row = new offer docx + pdf
    new_log_rows = []
    for (index_cust, row_cust) in new_data_frame_customer.iterrows():
        document = Document(word_template_path)
        custom_props = CustomProperties(document)

        row_prov = ""
        # First validate correct provider row count
        if len(new_data_frame_provider) != 1:
            raise ValueError(f"Provider count in {xls_offers_provider} must be exactly 1, got {len(new_data_frame_provider)}")
        # Now iterate once explicitly since validated
        row_prov = new_data_frame_provider.iloc[0]
        for column_name_prov in new_data_frame_provider.columns:
            custom_props.update(column_name_prov, row_prov[column_name_prov])
        for (column_name_cust, column_data_cust) in new_data_frame_customer.items():
            custom_props.update(column_name_cust, row_cust[column_name_cust])
        # For each row (offer)...
        base_document_to_save = build_base_document_to_save(row_prov, row_cust)
        save_updated_document(document, base_document_to_save)
        convert_to_pdf(base_document_to_save)

        # operation succeeded, append row to 'log' + drop row from 'new'
        log_data_frame = pd.concat([log_data_frame, row_cust.to_frame().T], axis='index', ignore_index=True)
        new_data_frame_customer.drop(labels=[index_cust], axis='index', inplace=True)

    # Update log sheet w fresh offer
    save_to_excel(new_data_frame_customer, log_data_frame)


def save_to_excel(data_frame, log_data_frame):
    with pd.ExcelWriter(xls_offers_log, mode='w', engine='openpyxl') as log_writer:
        log_data_frame.to_excel(log_writer, sheet_name=xls_offers_log_sheetname, index=False)
    with pd.ExcelWriter(xls_offers_customer, mode='w', engine='openpyxl') as cust_writer:
        data_frame.to_excel(cust_writer, sheet_name=xls_offers_customer_sheetname, index=False)
    return log_data_frame


def convert_to_pdf(base_document):
    save_as_docx = base_document + ".docx"
    save_as_pdf = base_document + ".pdf"
    try:
        # Convert the output
        convert(save_as_docx, save_as_pdf)
        print("Word file: " + save_as_docx)
        print("converted to Pdf file: " + save_as_pdf)
        logging.info(f"Successfully converted {save_as_docx} to PDF")
    except Exception as e:
        logging.error(f"Failed to convert {save_as_docx} to PDF: {e}")
        if os.path.exists(save_as_docx):  # to avoid stale files
            logging.info(f"Cleaning up incomplete conversion file {save_as_docx}")
            os.remove(save_as_docx)
        raise


def save_updated_document(document, base_document):
    save_as_docx = base_document + ".docx"
    try:
        # Save the output
        document.save(save_as_docx)
        print("Word file " + save_as_docx + " metadata is updated")
    except Exception as e:
        logging.error(f"Document not saved properly ({save_as_docx}): {e}")
        raise

def sanitize_filename(filename_part):
    return re.sub(r'[*<>:"/\\|?]', '_', filename_part).strip()


def build_base_document_to_save(row_prov, row_cust):
    def safe_get(row, column_name, default='unknown'):
        return sanitize_filename(str(row[column_name]).strip()) if column_name in row else default

    leverancier_naam = safe_get(row_prov, "Leverancier Naam")
    klant_naam = safe_get(row_cust, "Klant Naam")
    klant_job_title = safe_get(row_cust, "Klant JobTitle")
    klant_job_reference = safe_get(row_cust, "Klant JobReference")
    base_document = f"{base_output_document_path} - {leverancier_naam} - {klant_naam} - {klant_job_title} - {klant_job_reference}"
    return base_document


if __name__ == '__main__':
    _main()
