import os

# Generate once securely
hmac_secret = os.urandom(32)  # Save this permanently & securely for hashing!

print(hmac_secret)