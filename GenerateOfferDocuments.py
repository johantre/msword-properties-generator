from utils_docx import update_custom_properties_docx_structure
from utils_xlsx import extract_combined_replacements_from_xls
from utils_pdf import convert_to_pdf
from utils_mail import send_email
from dropbox.exceptions import AuthError
from utils_dropbox import dropbox_upload
import argparse
import logging
import sys
import os


# Remove any existing handlers explicitly:
handlers = logging.root.handlers[:]
for handler in handlers:
    logging.root.removeHandler(handler)

logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO').upper(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)


def _main(verbose=False, optional_args=None):
    logging.getLogger().handlers[0].flush()  # explicitly flush the output clearly

    combined_replacements = extract_combined_replacements_from_xls(optional_args)

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
                base_document_to_save = update_custom_properties_docx_structure(base_document_to_save, customer_line, provider_line)

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
