from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload
from dropbox.files import SharedLink
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
            # Set up the Selenium WebDriver (e.g., for Chrome)
            options = webdriver.ChromeOptions()
            # options.add_argument('--headless')  # Run in headless mode (without browser UI)
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            service = ChromeService(executable_path='/usr/local/bin/chromedriver')  # Update with your path to chromedriver
            driver = webdriver.Chrome(service=service, options=options)
            driver.get(url)

            try:
                # Handle exactly two redirects before clicking the button
                wait = WebDriverWait(driver, 10)
                current_url = url
                redirect_count = 0
                max_redirects = 2

                while redirect_count < max_redirects:
                    time.sleep(1)  # Small delay to ensure the URL has changed
                    new_url = driver.current_url
                    logging.info(f"Redirected to: {new_url}")
                    if new_url == current_url:
                        break  # URL has stabilized
                    current_url = new_url
                    redirect_count += 1

                # Wait for the download button to appear
                button_visible = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Download"]')))

                if button_visible:
                    # Click the button to trigger the download
                    button_clickable = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Download"]')))

                    if button_clickable:
                        driver.execute_script("document.querySelector('button[aria-label=\"Download\"]').click();")
                        time.sleep(3)  # Wait for the download to start, adjust as necessary

                        # Check the current URL for the download link or handle the response
                        download_link = driver.current_url
                        logging.info(f"Found download link: {download_link}")

                        # Log the page source for debugging
                        page_source = driver.page_source
                        logging.debug(f"Page source after clicking download: {page_source}")

                        # Search for a direct download link in the page source
                        # Search for a direct download link in the page source
                        direct_download_link = None
                        image_pattern = re.compile(r'https://[^"]+\.(jpg|jpeg|png|gif)')
                        match = image_pattern.search(page_source)
                        if match:
                            direct_download_link = match.group(0)
                            logging.info(f"Found direct download link: {direct_download_link}")

                        # Check the current URL for the download link or handle the response
                        download_link = driver.current_url
                        logging.info(f"Found download link: {download_link}")

                        # Use requests to download the file
                        response = requests.get(download_link, allow_redirects=True)
                        response.raise_for_status()

                        logging.info(f"Logging the response headers: {response.headers}")

                        # Check if the response is redirecting to another URL
                        if response.history:
                            logging.info(f"Redirected to final URL: {response.url}")
                            download_link = response.url

                        if response.headers.get('Content-Type').startswith('image/'):
                            with open(destination, 'wb') as file:
                                file.write(response.content)
                            logging.info(f"✅ OneDrive '{url}' to '{destination}' download Complete")
                        else:
                            logging.error("🔴 Failed to download image from OneDrive. Unexpected content type.")
                            raise ValueError("Failed to download image from OneDrive. Unexpected content type.")
                    else:
                        logging.error("🔴 Download button is not clickable")
                        raise ValueError("Download button is not clickable")
                else:
                    logging.error("🔴 Download button is not visible")
                    raise ValueError("Download button is not visible")
            except Exception as e:
                logging.error(f"🔴 Error: {str(e)}")
                raise e  # Re-raise the exception to ensure the workflow step fails
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

