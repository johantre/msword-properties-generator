from msword_properties_generator.data.utils_db import init_db, create_table_if_not_exist, get_inputs_and_encrypt, insert_or_update_into_db, close_db_commit_push, commit_db
from msword_properties_generator.utils.utils_image import get_image_and_encrypt_to_image_folder
from msword_properties_generator.utils.utils_logging import setup_logging
import logging


def main():
    setup_logging()
    conn = None
    try:
        conn = init_db()
        create_table_if_not_exist(conn)
        encrypted_data = get_inputs_and_encrypt()
        get_image_and_encrypt_to_image_folder()
        insert_or_update_into_db(conn, encrypted_data)
        commit_db(conn)

    except Exception as e:
            logging.error("🛑 An error occurred, exiting.")
            raise  # Re-raise the exception if it's a normal exit
    finally:
        if conn is not None:
            close_db_commit_push(conn)

if __name__ == "__main__":
    main()