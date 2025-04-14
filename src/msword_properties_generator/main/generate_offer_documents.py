from msword_properties_generator.utils.util_config import config  # importing centralized config
from msword_properties_generator.data.utils_db import create_replacements_from_db
from msword_properties_generator.utils.utils_docx import update_custom_properties_docx_structure
from msword_properties_generator.utils.utils_pdf import convert_to_pdf
from msword_properties_generator.utils.utils_mail import send_email
from msword_properties_generator.utils.utils_dropbox import dropbox_upload
from msword_properties_generator.utils.utils_logging import setup_logging
from dropbox.exceptions import AuthError
import argparse
import logging



def _main(verbose=False, main_args=None):
    setup_logging()

    combined_replacements = extract_combined_replacements(main_args)

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
                    logging.debug(f"Provider: {key_prov}: {value_prov}")
            else:
                logging.warning(f"No provider dict found in line: {line[index]}")
        else:
            # Handling for all other items
            logging.debug(f"Running over combined_replacements. Item {index}: {key} -> {line}")
            if isinstance(line, dict):
                customer_line = line
                # For each customer row ...
                base_document_to_save = update_custom_properties_docx_structure(customer_line, provider_line)

                convert_to_pdf(base_document_to_save)

                for key_cust, value_cust in customer_line.items():
                    logging.debug(f"Customer(s): {key_cust}: {value_cust}")
            else:
                logging.warning(f"No customer dict found in line: {line[index]}")

        if base_document_to_save.strip():
            if main_args:
                leverancier_email = main_args["LeverancierEmail"]
            else:
                leverancier_email = 'johan_tre@hotmail.com'
            generated_files = [base_document_to_save + ".docx", base_document_to_save + ".pdf"]

            if leverancier_email:
                send_email(generated_files, leverancier_email, provider_line, customer_line)
            else:
                logging.info(f"✉️ℹ️Email not sent, as requested by user.")

            upload_dropbox = True
            if main_args:
                if not main_args["UploadDropbox"] == 'true':
                    upload_dropbox = False
                    logging.info(f"🔄ℹ️Not uploaded to Dropbox, as requested by user. Value option_args['UploadDropbox'] is: {main_args['UploadDropbox']}.")

            if upload_dropbox:
                try:
                    dropbox_upload(generated_files)
                except AuthError as ae:
                    logging.error(f"☁️❌ Authentication error while uploading dropbox: {ae}")
                    # Handle the authentication error, such as prompting for re-authentication
                except Exception as ee:
                    # Handle other possible exceptions
                    logging.error(f"🔄❌ An error occurred while uploading dropbox: {ee}")
            else:
                logging.info(f"🔄ℹ️Not uploaded to Dropbox Johan!")

def extract_combined_replacements(main_args):
    def merge_replacements(customer_replacements, provider_replacements):
        combined_replacements = {}
        for key, value in provider_replacements.items():
            combined_replacements[f"prov_{key}"] = value
        for key, value in customer_replacements.items():
            combined_replacements[f"cust_{key}"] = value
        return combined_replacements

    provider_replacements = create_replacements_from_db(main_args)
    customer_replacements = create_replacements_from_args(main_args)
    combined_replacements = merge_replacements(customer_replacements, provider_replacements)
    return combined_replacements

def create_replacements_from_args(main_args):
    def sanitize_spaces_to_variable_name(any_string):
        return any_string.replace(" ", "")

    prefix = 'cust'

    sanitized_dict = {}
    sanitized_row_dict = {
        sanitize_spaces_to_variable_name(k): v
        for k, v in main_args.items()
    }
    sanitized_dict[f"{prefix}_0"] = sanitized_row_dict
    return sanitized_dict

if __name__ == '__main__':
    # Parse command-line arguments clearly here
    parser = argparse.ArgumentParser(description="Generate Offer Documents with optional verbose logging, and optional customer arguments.")
    parser.add_argument("--klantNaam", help="Klant Naam")
    parser.add_argument("--klantJobTitle", help="Klant JobTitle")
    parser.add_argument("--klantJobReference", help="Klant JobReference")
    parser.add_argument("--leverancierEmail", help="Leverancier Email")
    parser.add_argument("--uploadDropbox", help="Upload Dropbox")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    if args.klantNaam and args.klantJobTitle and args.klantJobReference:
        main_args = {
            'KlantNaam': args.klantNaam,
            'KlantJobTitle': args.klantJobTitle,
            'KlantJobReference': args.klantJobReference,
            'LeverancierEmail': args.leverancierEmail,
            'UploadDropbox': args.uploadDropbox
        }
        _main(
            verbose=args.verbose,
            main_args=main_args
        )
    else:
        _main(
            verbose=args.verbose
        )
