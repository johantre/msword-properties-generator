from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload
from dropbox.files import SharedLink
from bs4 import BeautifulSoup
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
            session = requests.Session()
            response = session.get(url, allow_redirects=True)
            response.raise_for_status()

            logging.info(f"Redirected to {response.url}")
            logging.info(f"Response Headers: {response.headers}")
            logging.info(f"Content-Type: {response.headers.get('Content-Type')}")

            # If the response is HTML, parse it to find the actual download link
            if 'text/html' in response.headers.get('Content-Type', ''):
                soup = BeautifulSoup(response.content, 'html.parser')
                download_link = None

                # Look for a link or button with download attributes
                for link in soup.find_all('a', href=True):
                    logging.info("'a' found on page")
                    if 'download' in link.get('href'):
                        download_link = link['href']
                        break

                if not download_link:
                    for button in soup.find_all('button'):
                        logging.info("'button' found on page")
                        if 'download' in button.get('onclick', ''):
                            logging.info("'onclick' found for button")
                            download_link = button['onclick'].split("'")[1]
                            break

                if not download_link:
                    msg = "🔴 Download link not found in the HTML content"
                    logging.error(msg)
                    raise ValueError(msg)

            if response.headers.get('Content-Type').startswith('image/'):
                with open(destination, 'wb') as file:
                    file.write(response.content)
                logging.info(f"✅ OneDrive '{url}' to '{destination}' download Complete")
            else:
                msg = "🔴 Failed to download image from OneDrive. Unexpected content type."
                logging.error(msg)
                raise ValueError(msg)
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

