from msword_properties_generator.utils.util_config import config  # importing centralized config
from msword_properties_generator.utils.utils_hash_encrypt import hash, encrypt_image, decrypt_image
from msword_properties_generator.utils.utils_git import git_stage_commit_push, get_private_assets_repo
from msword_properties_generator.utils.utils_download import download_image
from typing import cast
from PIL import Image
import tempfile
import logging
import os


def get_image_and_encrypt_to_image_folder():
    inputs = {
        "LeverancierEmail": os.getenv('INPUT_LEVERANCIEREMAIL'),
        "LeverancierURLSignatureImage": os.getenv('INPUT_LEVERANCIERURLSIGNATUREIMAGE')
    }
    hashed_leverancier_email = hash(inputs["LeverancierEmail"])

    # first construct decrypt temp folder
    temp_download_dir = tempfile.mkdtemp()
    temp_download_image_path = os.path.join(temp_download_dir, "decrypted_image.png")
    
    try:
        download_image(inputs["LeverancierURLSignatureImage"], temp_download_image_path)
    except Exception as e:
        logging.error(f"📷🔴 Failed to download image from {inputs['LeverancierURLSignatureImage']}. Error: {e}")
        exit(1)  # Exit with non-zero status code to indicate failure

    # Check if the image is a properly decrypted image to encrypt
    try:
        if not is_image_properly_decrypted(temp_download_image_path):
            raise ImageDecryptionError("📷❌🔒 Image is not properly decrypted.")
    except ImageDecryptionError as e:
        logging.error(f"📷🔴 The file at {temp_download_image_path} is not a proper image. Most probably the download failed. "
                      f"Please check if the image is shared with read permission 'for anyone with the link'. Error: {e}")
        exit(1)  # Exit with non-zero status code to indicate failure

    # construct encrypted path
    repo_private_path = get_private_assets_repo().working_tree_dir
    target_hashed_image_path = os.path.join(repo_private_path, config["paths"]["image_signature_folder"], hashed_leverancier_email)
    encrypt_image(temp_download_image_path, target_hashed_image_path)

    # Convert absolute path to relative path
    repo_path = get_private_assets_repo().working_tree_dir
    if os.path.isabs(target_hashed_image_path):
        target_hashed_image_path = os.path.relpath(cast(str, target_hashed_image_path), repo_path)

    git_stage_commit_push(cast(str, target_hashed_image_path), commit_message=f"Added image {hashed_leverancier_email} to Git repository")

def get_image_and_decrypt_from_image_folder(leverancier_email: str):
    # first construct encrypted path
    image_encryption_path = os.path.join(get_private_assets_repo().working_tree_dir, config["paths"]["image_signature_folder"], hash(leverancier_email))

    # construct decrypt temp folder
    temp_decrypted_dir = tempfile.mkdtemp()
    temp_decrypted_path = os.path.join(temp_decrypted_dir, "decrypted_image.png")
    
    try:
        decrypt_image(image_encryption_path, temp_decrypted_path)
        is_image_properly_decrypted(temp_decrypted_path)
    except (Exception, ImageDecryptionError) as e:
        logging.error(f"📷❌ Failed to decrypt image: {e}")
        temp_decrypted_path = ""
    
    return temp_decrypted_path

def remove_from_image_folder_git_commit_push():
    # Construct the path to the encrypted image
    hashed_leverancier_email = hash(os.getenv('INPUT_LEVERANCIEREMAIL'))
    image_encrypted_folder = config["paths"]["image_signature_folder"]
    image_encryption_path = os.path.join(get_private_assets_repo().working_tree_dir, image_encrypted_folder, hashed_leverancier_email)

    if os.path.exists(image_encryption_path):
        # Explicitly remove the file from filesystem only (no git here!)
        os.remove(image_encryption_path)
        # Convert absolute path to relative path
        repo_path = get_private_assets_repo().working_tree_dir
        rel_image_encryption_path = image_encryption_path
        if os.path.isabs(image_encryption_path):
            rel_image_encryption_path = os.path.relpath(cast(str, image_encryption_path), repo_path)
        logging.info(f"📷✅ Image removed successfully from filesystem: {rel_image_encryption_path}")

        # Clearly delegate staging, commit and push to the helper method
        git_stage_commit_push(file_path=cast(str, image_encryption_path), commit_message=f"Removed image {hashed_leverancier_email} from Git repository")
    else:
        logging.warning(f"📷🔍❌ No image found to remove: {image_encryption_path}")

    return image_encrypted_folder

def is_image_properly_decrypted(image_path):
    try:
        # Attempt to open the image file
        with Image.open(image_path) as img:
            img.verify()  # Verify the image integrity

        logging.debug(f"📷✅🔓 The image at {image_path} is properly decrypted.")
        return True
    except (IOError, SyntaxError) as e:
        msg = f"📷❌🔓 The image at {image_path} is not properly decrypted: {e}"
        logging.error(msg)
        raise ImageDecryptionError(msg)

class ImageDecryptionError(Exception):
    def __init__(self, message="📷❌ Image isn't properly decrypted"):
        self.message = message
        super().__init__(self.message)
