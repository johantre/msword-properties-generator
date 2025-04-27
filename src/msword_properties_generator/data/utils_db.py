from msword_properties_generator.utils.utils_config import config  # importing centralized config
from msword_properties_generator.utils.utils_hash_encrypt import encrypt, decrypt, hash
from msword_properties_generator.utils.utils_git import git_stage_commit_push, get_repo_root
import logging
import sqlite3
import os
import re

def get_private_assets_path():
    current_repo_root = get_repo_root()
    properties_generator_folder = str(config["paths"]["private_assets_folder"])
    private_assets_path = os.path.join(os.path.dirname(current_repo_root), properties_generator_folder)
    return private_assets_path

def get_db_path():
    db_path = str(config["paths"]["db_path"])
    return os.path.join(get_private_assets_path(), db_path)

def init_db():
    # Connect to SQLite database
    conn = sqlite3.connect(get_db_path())
    return conn

def close_db_commit_push(connection):
    connection.close()
    db_path = get_db_path()
    # Convert absolute path to relative path
    repo_path = get_private_assets_path()
    if os.path.isabs(db_path):
        db_path = os.path.relpath(db_path, repo_path)

    git_stage_commit_push(db_path, commit_message=f"Committed and pushed {db_path} to Git repository")

def commit_db(connection):
    connection.commit()

def get_column_names(connection, table_name):
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 1;")

    # Get column names starting from the third column; 1st=id, 2nd=hashed_key
    columns = [desc[0] for desc in cursor.description][2:]
    return columns

def get_leverancierEmail_from_env():
    return os.environ.get('INPUT_LEVERANCIEREMAIL')

def check_leverancier_count(connection, leverancier_email):
    count = connection.execute("SELECT COUNT(*) FROM offer_providers WHERE HashedLeverancierEmail = ?", (hash(leverancier_email),)).fetchone()[0]
    return count

def get_inputs_and_encrypt():
    # Get inputs from environment variables
    inputs = {
        "LeverancierEmail": os.environ.get('INPUT_LEVERANCIEREMAIL'),
        "LeverancierNaam": os.environ.get('INPUT_LEVERANCIERNAAM'),
        "LeverancierStad": os.environ.get('INPUT_LEVERANCIERSTAD'),
        "LeverancierStraat": os.environ.get('INPUT_LEVERANCIERSTRAAT'),
        "LeverancierPostadres": os.environ.get('INPUT_LEVERANCIERPOSTADRES'),
        "LeverancierKandidaat": os.environ.get('INPUT_LEVERANCIERKANDIDAAT'),
        "LeverancierOpgemaaktte": os.environ.get('INPUT_LEVERANCIEROPGEMAAKTTE'),
        "LeverancierHoedanigheid": os.environ.get('INPUT_LEVERANCIERHOEDANIGHEID')
    }
    # Validate email format
    leverancier_email = get_leverancierEmail_from_env()
    if leverancier_email is None or not re.match(r"[^@]+@[^@]+\.[^@]+", leverancier_email):
        raise ValueError(f"Invalid email address: {hash(leverancier_email)}")
    # Sanitize inputs (remove leading/trailing spaces)
    sanitized_inputs = {k: v.strip() for k, v in inputs.items()}
    # Encrypt inputs
    encrypted_inputs = {k: encrypt(v) for k, v in sanitized_inputs.items()}

    return encrypted_inputs

def get_leverancier_dict(connection, leverancier_email):
    prefix = 'prov'

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM offer_providers where HashedLeverancierEmail = ?", (hash(leverancier_email),))
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        logging.warning(f"⚠️The provided table 'offer_providers' in database '{get_db_path()}' has no row for key {hash(leverancier_email)}. Please verify the contents, or add one if necessary.")
        replacements_dict = {}
    else:
        # Get column names starting from the third column
        columns = get_column_names(connection, 'offer_providers')

        replacements_dict = {}
        for index, row in enumerate(rows):
             decrypted_row = {
                 columns[i]: decrypt(value)
                 for i, value in enumerate(row[2:])
             }
             replacements_dict[f"{prefix}_{index}"] = decrypted_row
    return replacements_dict

# All DB manipulations below
def create_table_if_not_exist(connection):
    cursor = connection.cursor()
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
    connection.commit()

def insert_into_db(connection, leverancier_email, encrypted_inputs):
    cursor = connection.cursor()

    # Compute deterministic HMAC hash (hex encoded)
    hashed_leverancier_email_key = hash(leverancier_email)

    # Insert encrypted data into table
    cursor.execute('''
        INSERT INTO offer_providers (
            HashedLeverancierEmail, 
            LeverancierEmail, 
            LeverancierNaam, 
            LeverancierStad, 
            LeverancierStraat, 
            LeverancierPostadres, 
            LeverancierKandidaat, 
            LeverancierOpgemaaktte, 
            LeverancierHoedanigheid
            )
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
    logging.info(f"️🛢🔒 Data encrypted and inserted successfully with hashed key")
    connection.commit()
    cursor.close()

def update_into_db(connection, leverancier_email, encrypted_inputs):
    cursor = connection.cursor()

    fields = ", ".join([f"{key} = ?" for key in encrypted_inputs.keys()])
    params = list(encrypted_inputs.values()) + [hash(leverancier_email)]
    update_query = f"""
        UPDATE offer_providers 
        SET {fields}
        WHERE HashedLeverancierEmail = ?
    """
    # Execute update
    cursor.execute(update_query, params)
    logging.info(f"️🛢🔒Data encrypted and updated successfully with hashed key")
    connection.commit()
    cursor.close()

def insert_or_update_into_db(connection, encrypted_inputs):
    cursor = connection.cursor()

    leverancier_email = get_leverancierEmail_from_env()
    record_count = check_leverancier_count(connection, leverancier_email)

    if record_count > 1:
        cursor.close()
        raise ValueError("Multiple records found; update must target exactly one record.")
    elif record_count == 0:
        insert_into_db(connection, leverancier_email, encrypted_inputs)
        logging.debug(f"️🛢📥 Line added to database with hashed key: {hash(leverancier_email)}")
    elif record_count == 1:
        update_into_db(connection, leverancier_email, encrypted_inputs)
        logging.debug(f"️🛢✏️ Line updated from database with hashed key: {hash(leverancier_email)}")

    connection.commit()
    cursor.close()

def remove_provider(connection):
    cursor = connection.cursor()
    leverancier_email = get_leverancierEmail_from_env()
    hashed_leverancier_email = hash(leverancier_email)

    # Check if provider exists
    count = check_leverancier_count(connection, leverancier_email)
    if count == 0:
        logging.warning(f"No provider found with email: {hashed_leverancier_email}")
        return False

    # Delete the provider from the table
    cursor.execute("DELETE FROM offer_providers WHERE HashedLeverancierEmail = ?", (hashed_leverancier_email,))
    logging.info(f"🛢🗑️Provider with email {hashed_leverancier_email} removed successfully")
    connection.commit()
    cursor.close()
    return True

def create_replacements_from_db(optionals=None):
    conn = init_db()

    leverancier_email = optionals.get('LeverancierEmail') if optionals else None
    if not leverancier_email:
        raise ValueError("LeverancierEmail missing in 'optional_args'.")

    replacements_dict = get_leverancier_dict(conn, leverancier_email)

    conn.close()
    return replacements_dict


