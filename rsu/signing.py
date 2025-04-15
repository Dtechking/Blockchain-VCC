from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import json
import base64

def sign_data(data_dict):
    # Load RSU private key
    with open("keys/rsu_private_key.pem", "rb") as f:
        private_key = RSA.import_key(f.read())

    # Convert data to bytes
    data_bytes = json.dumps(data_dict, sort_keys=True).encode()
    digest = SHA256.new(data_bytes)

    # Sign the digest
    signature = pkcs1_15.new(private_key).sign(digest)

    return base64.b64encode(signature).decode()

