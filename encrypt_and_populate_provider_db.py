from cryptography.fernet import Fernet
import sqlite3
import hashlib
import hmac
import re
import os

# Load the encryption key from environment variables
cipher_suite = Fernet(os.getenv('ENCRYPTION_KEY'))
hmac_secret = os.getenv('HASHING_KEY')

# Get inputs from environment variables with sanitized keys
inputs = {
    "LeverancierEmail": os.getenv('INPUT_LEVERANCIEREMAIL'),
    "LeverancierNaam": os.getenv('INPUT_LEVERANCIERNAAM'),
    "LeverancierStad": os.getenv('INPUT_LEVERANCIERSTAD'),
    "LeverancierStraat": os.getenv('INPUT_LEVERANCIERSTRAAT'),
    "LeverancierPostadres": os.getenv('INPUT_LEVERANCIERPOSTADRES'),
    "LeverancierKandidaat": os.getenv('INPUT_LEVERANCIERKANDIDAAT'),
    "LeverancierOpgemaaktte": os.getenv('INPUT_LEVERANCIEROPGEMAAKTTE'),
    "LeverancierHoedanigheid": os.getenv('INPUT_LEVERANCIERHOEDANIGHEID')
}

# Validate email format
leverancier_email = inputs.get("LeverancierEmail")
if leverancier_email is None or not re.match(r"[^@]+@[^@]+\.[^@]+", leverancier_email):
    raise ValueError(f"Invalid email address: {leverancier_email}")

print(f"Print inputs to debug")
for key, value in inputs.items():
    print(f"{key}: {value}")

# Sanitize inputs (remove leading/trailing spaces)
sanitized_inputs = {k: v.strip() for k, v in inputs.items()}

print(f"Print sanitized inputs to debug")
for key, value in sanitized_inputs.items():
    print(f"{key}: {value}")

# Compute deterministic HMAC hash (hex encoded)
hashed_leverancier_email_key = hmac.new(hmac_secret.encode(), leverancier_email.encode(), hashlib.sha256).hexdigest()

# Encrypt inputs
encrypted_inputs = {k: cipher_suite.encrypt(v.encode()).decode() for k, v in sanitized_inputs.items()}

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('res/offers_provider.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS offer_providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    HashedLeverancierEmail TEXT NOT NULL,
    LeverancierEmail TEXT NOT NULL,
    LeverancierNaam TEXT NOT NULL,
    LeverancierStad TEXT NOT NULL,
    LeverancierStraat TEXT NOT NULL,
    LeverancierPostadres TEXT NOT NULL,
    LeverancierKandidaat TEXT NOT NULL,
    LeverancierOpgemaaktte TEXT NOT NULL,
    LeverancierHoedanigheid TEXT NOT NULL
)
''')

# Insert encrypted data into table
cursor.execute('''
INSERT INTO offer_providers (HashedLeverancierEmail, LeverancierEmail, LeverancierNaam, LeverancierStad, LeverancierStraat, LeverancierPostadres, LeverancierKandidaat, LeverancierOpgemaaktte, LeverancierHoedanigheid)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    hashed_leverancier_email_key,
    encrypted_inputs['LeverancierEmail'],
    encrypted_inputs['LeverancierNaam'],
    encrypted_inputs['LeverancierStad'],
    encrypted_inputs['LeverancierStraat'],
    encrypted_inputs['LeverancierPostadres'],
    encrypted_inputs['LeverancierKandidaat'],
    encrypted_inputs['LeverancierOpgemaaktte'],
    encrypted_inputs['LeverancierHoedanigheid']
))

# Commit and close
conn.commit()
conn.close()

print("Data encrypted and inserted successfully with hashed key")