from util_config import config  # importing centralized config
from dropbox.exceptions import ApiError
from dropbox.files import WriteMode
import dropbox
import logging
import os



# Dropbox API setup for uploading to Dropbox Johan:
def get_dbx_client():
    APP_KEY = os.environ.get('DROPBOX_APP_KEY')
    APP_SECRET = os.environ.get('DROPBOX_APP_SECRET')
    REFRESH_TOKEN = os.environ.get('DROPBOX_REFRESH_TOKEN')

    return dropbox.Dropbox(
        oauth2_refresh_token=REFRESH_TOKEN,
        app_key=APP_KEY,
        app_secret=APP_SECRET
    )

def dropbox_upload(generated_files):
    dbx = get_dbx_client()

    for filepath in generated_files:
        abs_full_path = os.path.abspath(filepath)
        if os.path.exists(filepath):
            logging.debug(f"ℹ️File at location '{filepath}' found, at absolute path {abs_full_path}")
        else:
            logging.warning(f"⚠️File at location '{filepath}' not found, at absolute path {abs_full_path}!")

        dropbox_dest_path = os.path.join(config["dropbox"]["dropbox_destination_folder"], os.path.basename(filepath)).replace('\\', '/')

        logging.debug(f"📂 Local file to upload: {abs_full_path}")
        logging.debug(f"📌 Dropbox full destination path: {dropbox_dest_path}")
        with open(abs_full_path, 'rb') as file:
            try:
                logging.debug(f"📤 Uploading '{filepath}' to '{dropbox_dest_path}' on Dropbox.")
                response = dbx.files_upload(
                    file.read(),
                    dropbox_dest_path,
                    mode=WriteMode("overwrite")
                )
                logging.debug(f"🚀 Successfully uploaded file. Dropbox file details: {response}")
                logging.info(f"✅ Successfully uploaded file to Dropbox: '{os.path.basename(filepath)}'")
            except dropbox.exceptions.ApiError as err:logging.error(f"📛 Dropbox API error: {err}")


