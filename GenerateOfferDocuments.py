from docxcompose.properties import CustomProperties
from docx2pdf import convert
from docx import Document
import pandas as pd

# Path constructions
resource_path = 'res/'
output_path = 'output/'
excel_file_path = resource_path + 'Offers.xlsx'
base_document_name = 'Recht om te vertegenwoordigen'
word_template_path = resource_path + base_document_name + '.docx'
base_output_document_path = output_path + base_document_name


def _main():
    document = Document(word_template_path)

    # Read the Excel file into a DataFrame
    new_data_frame = pd.read_excel(excel_file_path, 'new')
    log_data_frame = pd.read_excel(excel_file_path, 'log')

    # Each row = new offer docx + pdf
    for index, row in new_data_frame.iterrows():
        for (column_name, column_data) in new_data_frame.items():
            property_data = row[column_name]
            CustomProperties(document).update(column_name, property_data)
        # For each row (offer)...
        base_document_to_save = build_base_document_to_save(row)
        save_updated_document(document, base_document_to_save)
        convert_to_pdf(base_document_to_save)
        # Update log sheet w fresh offer
        log_data_frame = move_row_to_sheet(index, row, new_data_frame, log_data_frame)

    with pd.ExcelWriter(excel_file_path) as writer:
        new_data_frame.to_excel(writer, engine='xlsxwriter', sheet_name='new', index=False)
        log_data_frame.to_excel(writer, engine='xlsxwriter', sheet_name='log', index=False)


def move_row_to_sheet(index, row, new_data_frame, log_data_frame):
    # operation succeeded, append row to 'log' + drop row from 'new'
    log_data_frame = pd.concat([log_data_frame, row.to_frame().T], axis='index', ignore_index=True)
    log_data_frame.reindex()
    new_data_frame.drop(labels=[index], axis='index', inplace=True)
    return log_data_frame


def convert_to_pdf(base_document_to_save):
    save_as_docx = base_document_to_save + ".docx"
    save_as_pdf = base_document_to_save + ".pdf"
    convert(save_as_docx, save_as_pdf)
    print("Word file: " + save_as_docx)
    print("has been converted to Pdf file: " + save_as_pdf)


def save_updated_document(document, base_document_to_save):
    save_as_docx = base_document_to_save + ".docx"
    # Save the output
    document.save(save_as_docx)
    print("Word file " + save_as_docx + " metadata is updated")


def build_base_document_to_save(row):
    leverancier_naam = row["Leverancier Naam"]
    klant_naam = row["Klant Naam"]
    klant_job_title = row["Klant JobTitle"]
    klant_job_reference = row["Klant JobReference"]
    base_document = (base_output_document_path + " - " + leverancier_naam + " - " +
                     klant_naam + " - " + klant_job_title + " - " + klant_job_reference)
    return base_document


if __name__ == '__main__':
    _main()
