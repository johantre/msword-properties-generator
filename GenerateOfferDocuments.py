from docxcompose.properties import CustomProperties
from jproperties import Properties
from docx2pdf import convert
from docx import Document
import pandas as pd

# Fetch properties
configs = Properties()
with open('env/prod.properties', 'rb') as read_prop:
    configs.load(read_prop)

# Path constructions
resource_path = configs.get("path.resource").data
output_path = configs.get("path.output").data
excel_offers_log = resource_path + configs.get("base.excel.offers.log").data
excel_offers_provider = resource_path + configs.get("base.excel.offers.provider").data
excel_offers_customer = resource_path + configs.get("base.excel.offers.customer").data
base_document_name = configs.get("base.word.template").data
word_template_path = resource_path + base_document_name + '.docx'
base_output_document_path = output_path + base_document_name


def _main():
    document = Document(word_template_path)

    # Read the Excel files into a DataFrames
    log_data_frame = pd.read_excel(excel_offers_log, 'log')
    new_data_frame_provider = pd.read_excel(excel_offers_provider, 'new')
    new_data_frame_customer = pd.read_excel(excel_offers_customer, 'new')

    # Each row = new offer docx + pdf
    for (index_cust, row_cust) in new_data_frame_customer.iterrows():
        last_row_prov = ""    # to initialise w correct type?
        for (index_prov, row_prov) in new_data_frame_provider.iterrows():
            for (column_name_prov, column_data_prov) in new_data_frame_provider.items():
                CustomProperties(document).update(column_name_prov, row_prov[column_name_prov])
                last_row_prov = row_prov
            if index_prov > 0:
                raise ValueError(f"provider count in " + excel_offers_provider + " is supposed to be only 1, got more")
        for (column_name_cust, column_data_cust) in new_data_frame_customer.items():
            CustomProperties(document).update(column_name_cust, row_cust[column_name_cust])
        # For each row (offer)...
        base_document_to_save = build_base_document_to_save(last_row_prov, row_cust)
        save_updated_document(document, base_document_to_save)
        convert_to_pdf(base_document_to_save)
        # Update log sheet w fresh offer
        log_data_frame = move_row_to_log(index_cust, row_cust, new_data_frame_customer, log_data_frame)


def move_row_to_log(index, row, data_frame, log_data_frame):
    # operation succeeded, append row to 'log' + drop row from 'new'
    log_data_frame = pd.concat([log_data_frame, row.to_frame().T], axis='index', ignore_index=True)
    log_data_frame.reindex()
    data_frame.drop(labels=[index], axis='index', inplace=True)

    with pd.ExcelWriter(excel_offers_log) as log_writer:
        log_data_frame.to_excel(log_writer, engine='xlsxwriter', sheet_name='log', index=False)
    with pd.ExcelWriter(excel_offers_customer) as cust_writer:
        data_frame.to_excel(cust_writer, engine='xlsxwriter', sheet_name='new', index=False)
    return log_data_frame


def convert_to_pdf(base_document):
    save_as_docx = base_document + ".docx"
    save_as_pdf = base_document + ".pdf"
    # Convert the output
    convert(save_as_docx, save_as_pdf)
    print("Word file: " + save_as_docx)
    print("converted to Pdf file: " + save_as_pdf)


def save_updated_document(document, base_document):
    save_as_docx = base_document + ".docx"
    # Save the output
    document.save(save_as_docx)
    print("Word file " + save_as_docx + " metadata is updated")


def build_base_document_to_save(row_prov, row_cust):
    leverancier_naam = str(row_prov["Leverancier Naam"]).strip()
    klant_naam = str(row_cust["Klant Naam"]).strip()
    klant_job_title = str(row_cust["Klant JobTitle"]).strip()
    klant_job_reference = str(row_cust["Klant JobReference"]).strip()
    base_document = (base_output_document_path + " - " + leverancier_naam + " - " +
                     klant_naam + " - " + klant_job_title + " - " + klant_job_reference)
    return base_document


if __name__ == '__main__':
    _main()
