from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload
from dropbox.files import SharedLink
from selenium.webdriver.common.by import By
from selenium import webdriver
import time
import dropbox
import requests
import logging
import io
import os
import re



GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REFRESH_TOKEN = os.getenv('GOOGLE_REFRESH_TOKEN')

DROPBOX_APP_KEY = os.getenv('DROPBOX_APP_KEY')
DROPBOX_APP_SECRET = os.getenv('DROPBOX_APP_SECRET')
DROPBOX_REFRESH_TOKEN = os.getenv('DROPBOX_REFRESH_TOKEN')


def detect_host(url):
    if 'drive.google.com' in url:
        return 'gdrive'
    elif 'dropbox.com' in url:
        return 'dropbox'
    elif '1drv.ms' in url or 'onedrive.live.com' in url:
        return 'onedrive'
    else:
        return 'unknown'

def download_image(url: str, destination: str):
    host = detect_host(url)

    try:
        if host == 'gdrive':
            file_id_match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
            if not file_id_match:
                raise ValueError("Invalid Google Drive URL.")
            file_id = file_id_match.group(1)

            google_drive_service = get_google_drive_service()
            request = google_drive_service.files().get_media(fileId=file_id)
            fh = io.FileIO(destination, mode='wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                logging.info(f'✅ Google Drive: {int(status.progress() * 100)}% to "{destination}"download Complete')

        elif host == 'dropbox':
            dropbox_service = get_dropbox_service()
            shared_link = dropbox.files.SharedLink(url=url)
            metadata, res = dropbox_service.sharing_get_shared_link_file(shared_link.url)
            with open(destination, "wb") as f:
                f.write(res.content)
            logging.info(f'✅ Dropbox: from "{metadata.name}" to "{destination}" download Complete')

        elif host == 'onedrive':
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')  # Run in headless mode (without browser UI)
            driver = webdriver.Chrome(options=options)  # Ensure chromedriver is in your PATH or provide the executable path
            driver.get(url)

            try:
                # Wait for the button to appear (adjust time as necessary)
                time.sleep(3)

                # Find the download button
                button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Download"]')

                if button:
                    # Click the button to trigger the download
                    button.click()
                    time.sleep(3)  # Wait for the download to start, adjust as necessary

                    # Check for the download link, assuming it appears in the page
                    download_link = driver.current_url
                    logging.info(f"Found download link: {download_link}")

                    # Use requests to download the file
                    response = requests.get(download_link, allow_redirects=True)
                    response.raise_for_status()

                    if response.headers.get('Content-Type').startswith('image/'):
                        with open(destination, 'wb') as file:
                            file.write(response.content)
                        logging.info(f"✅ OneDrive '{url}' to '{destination}' download Complete")
                    else:
                        msg = "🔴 Failed to download image from OneDrive. Unexpected content type."
                        logging.error(msg)
                        raise ValueError(msg)
                else:
                    msg = f"🔴 Download button not found"
                    logging.error(msg)
                    raise ValueError(msg)
            except Exception as e:
                logging.error(f"Error: {str(e)}")
                raise e
            finally:
                driver.quit()
        else:
            msg = f"🔴 Unsupported host/type for URL provided: {url}"
            logging.error(msg)
            raise ValueError(msg)
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise e

def get_google_drive_service():
    # Build credential explicitly from provided refresh token and client details
    google_creds = Credentials(
        token=None,  # initially None, SDK gets this auto-refreshed by refresh token
        refresh_token=GOOGLE_REFRESH_TOKEN,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET
    )
    try:
        google_creds.refresh(Request())  # explicitly auto-refresh if access token required
    except Exception as e:
        logging.error("🔴 Error explicitly when refreshing Google credentials:", e)
        exit(1)

    return build('drive', 'v3', credentials=google_creds)

def get_dropbox_service():
    return dropbox.Dropbox(
        oauth2_refresh_token=DROPBOX_REFRESH_TOKEN,
        app_key=DROPBOX_APP_KEY,
        app_secret=DROPBOX_APP_SECRET
    )

