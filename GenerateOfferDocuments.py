from email.message import EmailMessage
from jproperties import Properties
from docx2pdf import convert
from docx import Document
from lxml import etree as ET
import pandas as pd
import subprocess
import argparse
import tempfile
import logging
import smtplib
import zipfile
import shutil
import sys
import re
import os

# Fetch properties
try:
    configs = Properties()
    with open('env/prod.properties', 'rb') as read_prop:
        configs.load(read_prop)
except (FileNotFoundError, Exception) as e:
    logging.error(f"❌Error reading properties file: {e}")
    raise SystemExit(e)

# Mail constructions
mail_smtp_port = configs.get("mail.smtp_port").data
mail_smtp_server = configs.get("mail.smtp_server").data
mail_sender_email = configs.get("mail.sender_email").data
# Path constructions
resource_path = configs.get("path.resource").data
output_path = configs.get("path.output").data
image_file_path = os.path.join(resource_path, configs.get("path.resource.image_signature").data)
xls_offers_log = os.path.join(resource_path, configs.get("base.excel.offers.log").data)
xls_offers_log_sheetname = configs.get("base.excel.offers.log.sheetname").data
xls_offers_provider = os.path.join(resource_path, configs.get("base.excel.offers.provider").data)
xls_offers_provider_sheetname = configs.get("base.excel.offers.provider.sheetname").data
xls_offers_customer = os.path.join(resource_path, configs.get("base.excel.offers.customer").data)
xls_offers_customer_sheetname = configs.get("base.excel.offers.customer.sheetname").data
base_document_name = configs.get("base.word.template").data
base_document_namespace_cp = configs.get("base.word.namespace.cp").data
base_document_namespace_vt = configs.get("base.word.namespace.vt").data
base_document_image_alt_text_left =  configs.get("base.word.template.image_alt_text_left").data
base_document_image_alt_text_right =  configs.get("base.word.template.image_alt_text_right").data

word_template_path =  os.path.join(resource_path, base_document_name + '.docx')
base_output_document_path = os.path.join(output_path, base_document_name)

# Remove any existing handlers explicitly:
handlers = logging.root.handlers[:]
for handler in handlers:
    logging.root.removeHandler(handler)

# Explicitly set up root logger clearly once, explicitly:
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Now all logging calls explicitly will appear clearly:
logging.debug("🐞 Explicit debug from root setup. Explicitly visible now?")
logging.info("✅ Explicit info from root setup explicitly clearly visible now.")


def _main(verbose=False):
    logging.debug("🐞 Explicit debug logging clearly enabled.")
    logging.info("ℹ️ Explicit info logging clearly visible.")
    logging.warning("⚠️ Explicit warning logging clearly shown.")
    logging.error("❌ Explicit error logging clearly available.")
    logging.critical("🔥 Explicit critical logging clearly activated.")
    logging.getLogger().handlers[0].flush()  # explicitly flush the output clearly

    # Read the Excel files into a DataFrames
    log_data_frame = safely_read_excel(xls_offers_log, xls_offers_log_sheetname, "offers log")

    provider_data_frame = safely_read_excel(xls_offers_provider, xls_offers_provider_sheetname, "offers provider")
    provider_replacements = create_sanitized_replacements(xls_offers_provider, xls_offers_provider_sheetname)

    customers_data_frame = safely_read_excel(xls_offers_customer, xls_offers_customer_sheetname, "offers customer")
    customer_replacements = create_sanitized_replacements(xls_offers_customer, xls_offers_customer_sheetname)

    combined_replacements = {**customer_replacements, **provider_replacements}

    # Each row in offersCustomer = new offer docx + pdf
    for (index_cust, row_cust) in customers_data_frame.iterrows():
        # For each customer row ...
        # In the custom properties xml structure...
        extracted_dir = extract_docx(word_template_path)
        row_prov = set_custom_properties(extracted_dir, provider_data_frame, row_cust)
        base_document_to_save = build_base_document_to_save(row_prov, row_cust)
        repack_docx(extracted_dir, base_document_to_save)

        # In the document itself...
        document = open_document(base_document_to_save)
        replace_images(document)
        replace_direct_text(document, combined_replacements)
        save_document(base_document_to_save, document)

        convert_to_pdf(base_document_to_save)

        # operation succeeded, append row to 'log' + drop row from 'new'
        log_data_frame = pd.concat([log_data_frame, row_cust.to_frame().T], axis='index', ignore_index=True)
        customers_data_frame.drop(labels=[index_cust], axis='index', inplace=True)

        recipient_email = 'johan_tre@hotmail.com'
        generated_files = [base_document_to_save + ".docx", base_document_to_save + ".pdf"]

        send_email(generated_files, recipient_email)

    # Update log sheet w fresh offer
    save_to_excel(customers_data_frame, log_data_frame)


def send_email(generated_files, email_address):
    # Email setup (fill properly!)
    sender_password = os.getenv("APP_PASS_MAIL")
    if sender_password is None:
        raise EnvironmentError("❗ APP_PASS_MAIL environment variable is not set. "
                               "Please set this environment variable locally or via GitHub Secrets, or on your local environment as an environment variable.")

    email_subject = f"Offer documents are ready"
    email_body = f"Please find attached the offer documents."
    email_message = EmailMessage()
    email_message['Subject'] = email_subject
    email_message['From'] = mail_sender_email
    email_message['To'] = email_address
    email_message.set_content(email_body)

    for filepath in generated_files:
        if os.path.exists(filepath):
            abs_full_path = os.path.abspath(filepath)
            logging.info(f"ℹ️File at location {filepath} found, at absolute path {abs_full_path}")
        else:
            raise ValueError(f"❌File at location {filepath} not found!")

        file_basename = os.path.basename(filepath)
        with open(filepath, 'rb') as file:
            file_data = file.read()

            # Choosing the right MIME type explicitly for each file
            if filepath.endswith('.xlsx'):
                maintype, subtype = 'application', 'vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif filepath.endswith('.docx'):
                maintype, subtype = 'application', 'vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif filepath.endswith('.pdf'):
                maintype, subtype = 'application', 'pdf'
            else:
                maintype, subtype = 'application', 'octet-stream'

            email_message.add_attachment(
                file_data,
                maintype=maintype,
                subtype=subtype,
                filename=file_basename
            )
    # Send email securely
    try:
        with smtplib.SMTP(mail_smtp_server, mail_smtp_port) as smtp:
            smtp.starttls()
            smtp.login(mail_sender_email, sender_password)
            smtp.send_message(email_message)
        print('✅ Email successfully sent.')
    except Exception as e:
        print('❗ An error occurred:', e)


def set_custom_properties(extracted_dir, provider_data_frame, row_cust):
    # First validate correct provider row count
    if len(provider_data_frame) != 1:
        raise ValueError(f"❌Provider count in {xls_offers_provider} must be exactly 1, got {len(provider_data_frame)}")
    # Now iterate once explicitly since validated
    row_prov = provider_data_frame.iloc[0]
    for column_name_prov in provider_data_frame.columns:
        set_custom_property(extracted_dir, column_name_prov, row_prov[column_name_prov])
    # Customer replacements (the part you asked about previously)
    for column_name_cust, column_value_cust in row_cust.items():
        set_custom_property(extracted_dir, column_name_cust, column_value_cust)
    return row_prov


def set_custom_property(extracted_dir, property_name, property_value):
    custom_props_path = os.path.join(extracted_dir, 'docProps', 'custom.xml')

    tree = ET.parse(custom_props_path)
    root = tree.getroot()

    namespaces = {
        'cp': base_document_namespace_cp,
        'vt': base_document_namespace_vt
    }

    prop = None
    for p in root.findall('cp:property', namespaces):
        if p.get('name') == property_name:
            prop = p
            break

    if prop is not None:
        vt_elem = next(iter(prop))
        vt_elem.text = str(property_value)
    else:
        prop_ids = [int(p.get('pid')) for p in root.findall('cp:property', namespaces)]
        new_pid = max(prop_ids, default=1) + 1

        prop = ET.SubElement(root, '{%s}property' % namespaces['cp'], name=property_name,
                             pid=str(new_pid), fmtid='{D5CDD505-2E9C-101B-9397-08002B2CF9AE}')
        vt_elem = ET.SubElement(prop, '{%s}lpwstr' % namespaces['vt'])
        vt_elem.text = str(property_value)

    tree.write(custom_props_path, encoding='UTF-8', xml_declaration=True, standalone=True)


def extract_docx(docx_path):
    extracted_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(docx_path, 'r') as docx_zip:
        docx_zip.extractall(extracted_dir)
    return extracted_dir

def repack_docx(extracted_dir, base_document):
    save_as_docx = base_document + ".docx"
    output_docx_path = os.path.abspath(save_as_docx)
    with zipfile.ZipFile(output_docx_path, 'w', zipfile.ZIP_DEFLATED) as docx_zip:
        for foldername, subfolders, filenames in os.walk(extracted_dir):
            for filename in filenames:
                abs_name = os.path.join(foldername, filename)
                arc_name = os.path.relpath(abs_name, extracted_dir)
                docx_zip.write(abs_name, arc_name)
    shutil.rmtree(extracted_dir)


def create_sanitized_replacements(excel_filepath, sheet_name):
    df = pd.read_excel(excel_filepath, sheet_name=sheet_name, header=0)
    if df.empty:
        logging.warning(f"⚠️The provided Excel file '{excel_filepath}' with sheet '{sheet_name}' is empty, No data tor process. Please verify the contents.")
        sanitized_dict = {
            sanitize_spaces_to_variable_name(column_name): ''
            for column_name in df.columns
        }
    else:
        excel_dict = df.iloc[0].to_dict()
        # Here we sanitize KEYS ONLY exactly as you require
        sanitized_dict = {
            sanitize_spaces_to_variable_name(k): v
            for k, v in excel_dict.items()
        }
    return sanitized_dict


def replace_direct_text(document, replacements):
    def replace_in_paragraph(paragraph, replacements):
        for run in paragraph.runs:
            for old, new in replacements.items():
                if old in run.text:
                    run.text = run.text.replace(old, new)
                    logging.info(f"ℹ️'{old}' successfully replaced by '{new}' in target file in paragraphs")

    # Replace in paragraphs
    for paragraph in document.paragraphs:
        replace_in_paragraph(paragraph, replacements)
    # Replace in tables (cells)
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    replace_in_paragraph(paragraph, replacements)
                    logging.info(f"ℹ️'{replacements}' in target file successfully replaced in tables")

def replace_images(document):
    replace_images_by_alt_text(document, base_document_image_alt_text_left, image_file_path)
    replace_images_by_alt_text(document, base_document_image_alt_text_right, image_file_path)

def replace_images_by_alt_text(doc, alt_text, new_image_path):
    with open(new_image_path, 'rb') as image_file:
        image_data = image_file.read()
    replaced = False
    for shape in doc.inline_shapes:
        doc_pr = shape._inline.docPr  # protected member accessed due to limitation of python-docx API
        if doc_pr.get('descr') == alt_text:
            rId = shape._inline.graphic.graphicData.pic.blipFill.blip.embed
            doc.part.related_parts[rId]._blob = image_data
            replaced = True
            pass
    if not replaced:
        logging.warning(f"⚠️No image found with alt_text '{alt_text}'")
    else:
        logging.info(f"ℹ️Image with alt_text '{alt_text}' in target file successfully replaced")


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


def convert_to_pdf(base_document):
    convert_from_docx = base_document + ".docx"
    save_as_pdf = base_document + ".pdf"

    if not os.path.exists(output_path):
        os.makedirs(output_path)
    try:
        subprocess.run([
            'soffice',
            '--headless',
            '--convert-to',
            'pdf',
            '--outdir',
            output_path,
            convert_from_docx
        ], check=True)
        abs_full_path_convert_from_docx = os.path.abspath(convert_from_docx)
        abs_full_path_save_as_pdf = os.path.abspath(save_as_pdf)
        logging.info("ℹ️Word file: " + convert_from_docx + " with absolute path: " + abs_full_path_convert_from_docx)
        logging.info("ℹ️Successfully converted to Pdf file: " + save_as_pdf + " with absolute path: " + abs_full_path_save_as_pdf)
    except subprocess.CalledProcessError as e:
        logging.error(f"❌Could not convert PDF: {e}")

def convert_to_pdf_traditional(base_document):
    save_as_docx = base_document + ".docx"
    save_as_pdf = base_document + ".pdf"
    try:
        # Convert the output
        convert(save_as_docx, save_as_pdf)
        logging.info("ℹ️Word file: " + save_as_docx)
        logging.info("ℹ️Successfully converted to Pdf file: " + save_as_pdf)
    except Exception as e:
        logging.error(f"❌Failed to convert {save_as_docx} to PDF: {e}")
        if os.path.exists(save_as_docx):  # to avoid stale files
            logging.info(f"ℹ️Cleaning up incomplete conversion file {save_as_docx}")
            os.remove(save_as_docx)
        raise


def open_document(base_document):
    save_as_docx = base_document + ".docx"
    return Document(save_as_docx)

def save_document(base_document, document):
    save_as_docx = base_document + ".docx"
    document.save(save_as_docx)


def sanitize_filename(filename_part):
    return re.sub(r'[*<>:"/\\|?]', '_', filename_part).strip()

def sanitize_spaces_to_variable_name(any_string):
    return any_string.replace(" ", "")

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
    # Parse command-line arguments clearly here
    parser = argparse.ArgumentParser(description="Generate Offer Documents with optional verbose logging.")
    parser.add_argument('-v','--verbose', '-v', action='store_true', help='Enable clear verbose debug-level logs.')
    args = parser.parse_args()

    _main(verbose=args.verbose)

