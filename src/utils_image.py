from util_config import config  # importing centralized config
from utils_hash_encrypt import hash, encrypt_image, decrypt_image
from utils_download import download_image
from git import Repo, Actor, exc
from typing import cast
import tempfile
import os

def get_image_and_encrypt_to_image_folder():
    inputs = {
        "LeverancierEmail": os.getenv('INPUT_LEVERANCIEREMAIL'),
        "LeverancierURLSignatureImage": os.getenv('INPUT_LEVERANCIERURLSIGNATUREIMAGE')
    }
    temp_download_dir = tempfile.mkdtemp()
    temp_download_image_path = os.path.join(temp_download_dir, "decrypted_image.png")
    download_image(inputs["LeverancierURLSignatureImage"], temp_download_image_path)

    target_hashed_image_path = os.path.join(config["paths"]["image_signature_folder"], hash(inputs["LeverancierEmail"]))
    encrypt_image(temp_download_image_path, target_hashed_image_path)

    git_add_commit_and_push(cast(str, target_hashed_image_path))

def get_image_and_decrypt_from_image_folder(leverancier_email: str):
    # first construct encrypted path
    image_encryption_path = os.path.join(config["paths"]["image_signature_folder"], hash(leverancier_email))

    # decrypt to temp folder
    temp_decrypted_dir = tempfile.mkdtemp()
    temp_decrypted_path = os.path.join(temp_decrypted_dir, "decrypted_image.png")

    decrypt_image(image_encryption_path, temp_decrypted_path)
    return temp_decrypted_path


def git_add_commit_and_push(file_path: str, commit_message: str = "Automated commit of encrypted image"):
    try:
        # Get repository from current directory
        repo_path = os.getcwd()
        repo = Repo(repo_path)
        bot_author = Actor("github-actions[bot]", "github-actions[bot]@users.noreply.github.com")

        if repo.is_dirty(untracked_files=True):
            # Add file to Git index (stage file)
            repo.index.add([file_path])
            print(f"File added to Git index: {file_path}")

            # Commit changes
            repo.index.commit(commit_message, author=bot_author, committer=bot_author)
            print(f"Committed to Git: '{commit_message}'")

            # Push changes to remote repository
            origin = repo.remote(name='origin')
            origin.push()
            print("Push successful.")
        else:
            print("No changes to commit.")

    except exc.GitCommandError as e:
        print(f"Git command failed: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

