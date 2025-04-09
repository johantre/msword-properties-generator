from msword_properties_generator.data.utils_db import init_db, remove_provider, commit_db, close_db_commit_push
from msword_properties_generator.utils.utils_image import remove_from_image_folder_git_commit_push
from msword_properties_generator.utils.utils_logging import setup_logging



setup_logging()
conn = init_db()

remove_provider(conn)
remove_from_image_folder_git_commit_push()

# Commit and close
commit_db(conn)
close_db_commit_push(conn)
