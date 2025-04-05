from msword_properties_generator.data.utils_db import init_db, remove_provider
from msword_properties_generator.utils.utils_image import remove_from_image_folder


conn = init_db()

remove_provider(conn)
remove_from_image_folder()

# Commit and close
conn.commit()
conn.close()
