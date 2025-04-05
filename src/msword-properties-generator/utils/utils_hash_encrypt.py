from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.fernet import Fernet
import hashlib
import base64
import hmac
import os


def get_encryption_key():
    return os.getenv('ENCRYPTION_KEY')

def get_hash_key():
    return os.getenv('HASHING_KEY')

def get_cipher_suite():
    return Fernet(get_encryption_key())

def encrypt(to_encrypt_string):
    cipher_suite = get_cipher_suite()
    encrypted_string = cipher_suite.encrypt(to_encrypt_string.encode()).decode()
    return encrypted_string

def decrypt(to_decrypt_value):
    cipher_suite = get_cipher_suite()
    decrypted_string= cipher_suite.decrypt(to_decrypt_value.encode()).decode()
    return decrypted_string

def hash(to_hash_string):
    hmac_secret = get_hash_key()
    hashed_string = hmac.new(hmac_secret.encode(), to_hash_string.encode(), hashlib.sha256).hexdigest()
    return hashed_string

def encrypt_image(input_file, output_file):
    encryption_key = get_encryption_key()

    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(encryption_key.encode())

    with open(input_file, 'rb') as f:
        plaintext = f.read()

    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(plaintext) + padder.finalize()

    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    with open(output_file, 'wb') as f:
        f.write(base64.b64encode(salt + iv + ciphertext))

def decrypt_image(input_file, output_file):
    encryption_key = get_encryption_key()

    with open(input_file, 'rb') as f:
        encoded_data = f.read()

    data = base64.b64decode(encoded_data)
    salt = data[:16]
    iv = data[16:32]
    ciphertext = data[32:]

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(encryption_key.encode())

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

    with open(output_file, 'wb') as f:
        f.write(plaintext)