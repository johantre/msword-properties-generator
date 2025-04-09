from msword_properties_generator.utils.util_config import config  # importing centralized config
from msword_properties_generator.utils.utils_hash_encrypt import hash, encrypt_image, decrypt_image
from msword_properties_generator.utils.utils_download import download_image
from git import Repo, Actor, exc
from typing import cast
from PIL import Image
import tempfile
import logging
import git
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
    download_image(inputs["LeverancierURLSignatureImage"], temp_download_image_path)

    # Check if the image is a properly decrypted image to encrypt
    try:
        if not is_image_properly_decrypted(temp_download_image_path):
            raise ImageDecryptionError("Image is not properly decrypted.")
    except ImageDecryptionError as e:
        logging.error(f"The file at {temp_download_image_path} is not a proper image. Most probably the download failed. "
                      f"Please check if the image is shared with read permission 'for anyone with the link'. Error: {e}")
        exit(1)  # Exit with non-zero status code to indicate failure

    # construct encrypted path
    target_hashed_image_path = os.path.join(config["paths"]["image_signature_folder"], hashed_leverancier_email)
    encrypt_image(temp_download_image_path, target_hashed_image_path)

    # Convert absolute path to relative path
    repo_path = get_repo_root()
    if os.path.isabs(target_hashed_image_path):
        target_hashed_image_path = os.path.relpath(target_hashed_image_path, repo_path)    

    git_add_commit_and_push(cast(str, target_hashed_image_path), commit_message=f"Added image for {hashed_leverancier_email}")

def get_image_and_decrypt_from_image_folder(leverancier_email: str):
    # first construct encrypted path
    image_encryption_path = os.path.join(config["paths"]["image_signature_folder"], hash(leverancier_email))

    # construct decrypt temp folder
    temp_decrypted_dir = tempfile.mkdtemp()
    temp_decrypted_path = os.path.join(temp_decrypted_dir, "decrypted_image.png")
    decrypt_image(image_encryption_path, temp_decrypted_path)
    try:
        is_image_properly_decrypted(temp_decrypted_path)
    except ImageDecryptionError as e:
        logging.error(e)
        temp_decrypted_path = ""
    return temp_decrypted_path

def remove_from_image_folder_git_commit_push():
    # Construct the path to the encrypted image
    hashed_leverancier_email = hash(os.getenv('INPUT_LEVERANCIEREMAIL'))
    image_encrypted_folder = config["paths"]["image_signature_folder"]
    image_encryption_path = os.path.join(image_encrypted_folder, hashed_leverancier_email)

    if os.path.exists(image_encryption_path):
        # Explicitly remove the file from filesystem only (no git here!)
        os.remove(image_encryption_path)
        logging.info(f"Image removed successfully from filesystem: {image_encryption_path}")

        # Clearly delegate staging, commit and push to the helper method
        git_add_commit_and_push(
            file_path=str(image_encryption_path),
            commit_message=f"Removed image for {hashed_leverancier_email}"
        )
    else:
        logging.warning(f"No image found to remove: {image_encryption_path}")

    return image_encrypted_folder

def git_add_commit_and_push(file_path: str, commit_message: str = "Automated commit and push"):
    repo_path = get_repo_root()
    repo = Repo(repo_path)
    bot_author = Actor("github-actions[bot]", "github-actions[bot]@users.noreply.github.com")

    relative_file_path = os.path.relpath(file_path, repo_path)

    try:
        if relative_file_path.startswith("res/images/"):
            full_path = os.path.join(repo_path, relative_file_path)

            if os.path.exists(full_path):
                # File exists, stage addition or modification clearly
                repo.index.add([relative_file_path])
                logging.info(f"File staged explicitly for addition/update: {relative_file_path}")
            else:
                # File doesn't exist, fully stage removal via git CLI
                repo.git.rm(relative_file_path)
                logging.info(f"File staged explicitly for removal: {relative_file_path}")

            # commit staged changes
            repo.index.commit(commit_message, author=bot_author, committer=bot_author)
            logging.info(f"Committed to Git: '{commit_message}'")

            # push & verify the push
            origin = repo.remote('origin')
            push_result = origin.push()[0]
            if push_result.flags & push_result.ERROR:
                logging.error(f"Push failed: {push_result.summary}")
                raise RuntimeError(f"Push failed: {push_result.summary}")
            logging.info("Explicit push successful.")
        else:
            logging.debug(f"No action for non-image path: {file_path}")

    except exc.GitCommandError as e:
        logging.error(f"Explicit Git command error: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Explicit unexpected error: {str(e)}")
        raise

def is_image_properly_decrypted(image_path):
    try:
        # Attempt to open the image file
        with Image.open(image_path) as img:
            img.verify()  # Verify the image integrity

        logging.debug(f"✅ The image at {image_path} is properly decrypted.")
        return True
    except (IOError, SyntaxError) as e:
        msg = f"❌ The image at {image_path} is not properly decrypted: {e}"
        logging.error(msg)
        raise ImageDecryptionError(msg)

def get_repo_root():
    repo = git.Repo('.', search_parent_directories=True)
    repo_root = repo.git.rev_parse("--show-toplevel")
    return repo_root

class ImageDecryptionError(Exception):
    def __init__(self, message="Image isn't properly decrypted"):
        self.message = message
        super().__init__(self.message)
