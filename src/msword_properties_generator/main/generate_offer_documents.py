from msword_properties_generator.utils.util_config import config  # importing centralized config
from msword_properties_generator.data.utils_db import create_replacements_from_db
from msword_properties_generator.data.utils_xlsx import create_replacements_from_xls
from msword_properties_generator.utils.utils_docx import update_custom_properties_docx_structure
from msword_properties_generator.utils.utils_pdf import convert_to_pdf
from msword_properties_generator.utils.utils_mail import send_email
from msword_properties_generator.utils.utils_dropbox import dropbox_upload
from dropbox.exceptions import AuthError
from datetime import datetime, timezone
import argparse
import logging
import pytz
import os


class LocalTimezoneFormatter(logging.Formatter):
    default_time_format = "%Y-%m-%d %H:%M:%S %Z%z"
    local_timezone = pytz.timezone('Europe/Amsterdam')

    def formatTime(self, record, datefmt=None):
        utc_dt = datetime.fromtimestamp(record.created, timezone.utc)
        local_dt = utc_dt.astimezone(self.local_timezone)
        return local_dt.strftime(datefmt or self.default_time_format)

def setup_logging():
    LEVEL = os.environ.get("LOG_LEVEL", "INFO")

    handler = logging.StreamHandler()
    formatter = LocalTimezoneFormatter(fmt="%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LEVEL.upper(), "INFO"))

    # Important: clear existing handlers to avoid duplication
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.addHandler(handler)

def _main(verbose=False, optional_args=None):
    setup_logging()

    combined_replacements = extract_combined_replacements(optional_args)

    # Each row in offersCustomer = new offer docx + pdf
    provider_line = None
    base_document_to_save = None
    for index, (key, line) in enumerate(combined_replacements.items()):
        if index == 0:
            # Special handling for the first item
            logging.debug(f"Running over combined_replacements. First item: {key} -> {line}")
            if isinstance(line, dict):
                provider_line = line
                base_document_to_save = ""
                for key_prov, value_prov in provider_line.items():
                    logging.debug(f'Provider: {key_prov}: {value_prov}')
            else:
                logging.warning(f'No provider dict found in line: {line[index]}')
        else:
            # Handling for all other items
            logging.debug(f"Running over combined_replacements. Item {index}: {key} -> {line}")
            if isinstance(line, dict):
                customer_line = line
                # For each customer row ...
                base_document_to_save = update_custom_properties_docx_structure(customer_line, provider_line)

                convert_to_pdf(base_document_to_save)

                for key_cust, value_cust in customer_line.items():
                    logging.debug(f'Customer(s): {key_cust}: {value_cust}')
            else:
                logging.warning(f'No customer dict found in line: {line[index]}')

        if base_document_to_save.strip():
            if optional_args:
                recipient_email = optional_args["EmailRecipient"]
            else:
                recipient_email = 'johan_tre@hotmail.com'
            generated_files = [base_document_to_save + ".docx", base_document_to_save + ".pdf"]

            if recipient_email:
                send_email(generated_files, recipient_email, provider_line, customer_line)
            else:
                logging.info(f"ℹ️Email not sent, as requested by user.")

            upload_dropbox = True
            if optional_args:
                if not optional_args["UploadDropbox"] == 'true':
                    upload_dropbox = False
                    logging.info(f"ℹ️Not uploaded to Dropbox, as requested by user. Value option_args['UploadDropbox'] is: {optional_args["UploadDropbox"]}.")

            if upload_dropbox:
                try:
                    dropbox_upload(generated_files)
                except AuthError as ae:
                    logging.error(f"Authentication error while uploading dropbox: {ae}")
                    # Handle the authentication error, such as prompting for re-authentication
                except Exception as ee:
                    # Handle other possible exceptions
                    logging.error(f"An error occurred while uploading dropbox: {ee}")
            else:
                logging.info(f"ℹ️Not uploaded to Dropbox Johan!")

def extract_combined_replacements(optional_args):
    def merge_replacements(customer_replacements, provider_replacements):
        combined_replacements = {}
        for key, value in provider_replacements.items():
            combined_replacements[f'prov_{key}'] = value
        for key, value in customer_replacements.items():
            combined_replacements[f'cust_{key}'] = value
        return combined_replacements

    provider_replacements = create_replacements_from_db(optional_args)
    customer_replacements = create_replacements_from_xls(config["paths"]["xls_offers_customer"], config["paths"]["xls_offers_customer_sheetname"], optional_args)
    combined_replacements = merge_replacements(customer_replacements, provider_replacements)
    return combined_replacements


if __name__ == '__main__':
    # Parse command-line arguments clearly here
    parser = argparse.ArgumentParser(description="Generate Offer Documents with optional verbose logging, and optional customer arguments.")
    parser.add_argument("--klantNaam", help="Klant Naam")
    parser.add_argument("--klantJobTitle", help="Klant JobTitle")
    parser.add_argument("--klantJobReference", help="Klant JobReference")
    parser.add_argument("--emailRecipient", help="Email Recipient")
    parser.add_argument("--uploadDropbox", help="Upload Dropbox")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    if args.klantNaam and args.klantJobTitle and args.klantJobReference:
        optional_args = {
            'KlantNaam': args.klantNaam,
            'KlantJobTitle': args.klantJobTitle,
            'KlantJobReference': args.klantJobReference,
            'EmailRecipient': args.emailRecipient,
            'UploadDropbox': args.uploadDropbox
        }
        _main(
            verbose=args.verbose,
            optional_args=optional_args
        )
    else:
        _main(
            verbose=args.verbose
        )
