from cryptography.fernet import Fernet

# Generate a key
key = Fernet.generate_key()

# Print the key
print(key.decode())

# Optionally, save the key to a file (uncomment the lines below if you want to save it)
# with open("encryption_key.key", "wb") as key_file:
#     key_file.write(key)