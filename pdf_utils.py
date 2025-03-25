from jproperties import Properties
from docx2pdf import convert
import subprocess
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

output_path = configs.get("path.output").data


def convert_to_pdf(base_document):
    convert_from_docx = base_document + ".docx"
    save_as_pdf = base_document + ".pdf"

    if not os.path.exists(output_path):
        os.makedirs(output_path)
    abs_full_path_convert_from_docx = os.path.abspath(convert_from_docx)
    abs_full_path_save_as_pdf = os.path.abspath(save_as_pdf)
    abs_output_path = os.path.abspath(output_path)

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
        logging.debug("ℹ️Word file: " + convert_from_docx + " with absolute path: " + abs_full_path_convert_from_docx)
        logging.debug("ℹ️Successfully converted to Pdf file: " + save_as_pdf + " with absolute path: " + abs_full_path_save_as_pdf)
        files = os.listdir(abs_output_path)
        logging.debug(f"📂 Explicitly listing files from '{abs_output_path}':")
        if files:
            for file in files:
                logging.debug(f"    - {file}")
        else:
            logging.warning(f"📭 Directory '{abs_output_path}' explicitly exists but is empty!")
    except FileNotFoundError:
        logging.error(f"🚨 Directory '{abs_output_path}' not found!")
    except subprocess.CalledProcessError as e:
        logging.error(f"❌Could not convert PDF: {e}")

def convert_to_pdf_traditional(base_document):
    save_as_docx = base_document + ".docx"
    save_as_pdf = base_document + ".pdf"
    try:
        # Convert the output
        convert(save_as_docx, save_as_pdf)
        logging.debug("ℹ️Word file: " + save_as_docx)
        logging.debug("ℹ️Successfully converted to Pdf file: " + save_as_pdf)
    except Exception as e:
        logging.error(f"❌Failed to convert {save_as_docx} to PDF: {e}")
        if os.path.exists(save_as_docx):  # to avoid stale files
            logging.debug(f"ℹ️Cleaning up incomplete conversion file {save_as_docx}")
            os.remove(save_as_docx)
        raise

