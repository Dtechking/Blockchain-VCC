import time
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import base64

# Sample RSA public key for testing
SAMPLE_PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...
-----END PUBLIC KEY-----
"""

# Validates timestamp and digital signature
def validate_data(data):
    current_time = int(time.time())

    # Timestamp check (reject data older than 5 minutes)
    if abs(current_time - data['timestamp']) > 300:
        return False, "Outdated data"

    # Digital signature check
    try:
        public_key = RSA.import_key(SAMPLE_PUBLIC_KEY)
        signature = base64.b64decode(data['signature'])
        del data['signature']

        data_str = str(data).encode('utf-8')
        hashed_data = SHA256.new(data_str)

        pkcs1_15.new(public_key).verify(hashed_data, signature)
        return True, "Valid data"
    except Exception as e:
        return False, f"Signature verification failed: {str(e)}"
