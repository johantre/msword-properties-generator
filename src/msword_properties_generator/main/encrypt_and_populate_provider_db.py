from msword_properties_generator.data.utils_db import init_db, create_table_if_not_exist, get_inputs_and_encrypt, insert_or_update_into_db
from msword_properties_generator.utils.utils_image import get_image_and_encrypt_to_image_folder


# Connect to SQLite database (or create it if it doesn't exist)
conn = init_db()
create_table_if_not_exist(conn)

encrypted_inputs = get_inputs_and_encrypt()

get_image_and_encrypt_to_image_folder()

insert_or_update_into_db(conn, encrypted_inputs)

# Commit and close
conn.commit()
conn.close()
