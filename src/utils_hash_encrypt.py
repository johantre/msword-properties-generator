from cryptography.fernet import Fernet
import hashlib
import hmac
import os

def get_cipher_suite():
    return Fernet(os.getenv('ENCRYPTION_KEY'))

def get_hash_key():
    return os.getenv('HASHING_KEY')

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
