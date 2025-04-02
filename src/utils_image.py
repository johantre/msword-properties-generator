from util_config import config  # importing centralized config
from utils_hash_encrypt import hash, encrypt_image
import tempfile
import requests
import os


def download_image(url, local_path):
    response = requests.get(url)
    with open(local_path, 'wb') as f:
        f.write(response.content)

def get_image_and_encrypt_to_image_folder():
    inputs = {
        "LeverancierEmail": os.getenv('INPUT_LEVERANCIEREMAIL'),
        "LeverancierURLSignatureImage": os.getenv('INPUT_LEVERANCIERURLSIGNATUREIMAGE')
    }
    temp_download_dir = tempfile.mkdtemp()
    temp_download_image_path = os.path.join(temp_download_dir, "image.png")
    download_image(inputs["LeverancierURLSignatureImage"], temp_download_image_path)

    target_hashed_image_path = os.path.join(config["path"]["image_signature_folder"], hash(inputs["LeverancierEmail"]))
    encrypt_image(temp_download_image_path, target_hashed_image_path)

