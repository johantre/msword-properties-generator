from msword_properties_generator.utils.util_config import config  # importing centralized config
from docx2pdf import convert
import subprocess
import logging
import os


def convert_to_pdf(base_document):
    output_path = config["paths"]["output_path"]
    convert_from_docx = base_document + ".docx"
    save_as_pdf = base_document + ".pdf"

    if not os.path.exists(output_path):
        os.makedirs(output_path)
    abs_full_path_convert_from_docx = os.path.abspath(convert_from_docx)
    abs_full_path_save_as_pdf = os.path.abspath(save_as_pdf)
    abs_output_path = os.path.abspath(output_path)

    try:
        os.environ["SAL_LOG"] = "-all"  #mute soffice logging
        subprocess.run([
            'soffice',
            '--headless',
            '--nologo',
            '--convert-to',
            'pdf',
            '--outdir',
            output_path,
            convert_from_docx
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logging.debug("📄ℹ️ Word file: " + "docx name omitted for privacy" + " with absolute path: " + "docx name omitted for privacy")
        logging.debug("📄ℹ️ Successfully converted to Pdf file: " + "pdf name omitted for privacy" + " with absolute path: " + "pdf name omitted for privacy")
        files = os.listdir(abs_output_path)
        logging.debug(f"📂 Explicitly listing files from '{output_path}':")
        if files:
            for file in files:
                logging.debug(f"    - file name omitted for privacy")
        else:
            logging.warning(f"📭 Directory '{output_path}' explicitly exists but is empty!")
    except FileNotFoundError:
        logging.error(f"📄🚨 LibreOffice not found!")
    except subprocess.CalledProcessError as e:
        logging.error(f"📄❌ Could not convert PDF: {e}")
    else:
        logging.info(f"📄✅ LibreOffice executable ('soffice') IS found!")

def convert_to_pdf_traditional(base_document):
    save_as_docx = base_document + ".docx"
    save_as_pdf = base_document + ".pdf"
    try:
        # Convert the output
        convert(save_as_docx, save_as_pdf)
        logging.debug("📄ℹ️ Word file: " + "file name omitted for privacy")
        logging.debug("📄ℹ️ Successfully converted to Pdf file: " + "file name omitted for privacy")
    except Exception as e:
        logging.error(f"📄❌ Failed to convert 'file name omitted for privacy' to PDF: {e}")
        if os.path.exists(save_as_docx):  # to avoid stale files
            logging.debug(f"📄ℹ️ Cleaning up incomplete conversion file 'file name omitted for privacy'")
            os.remove(save_as_docx)
        raise
