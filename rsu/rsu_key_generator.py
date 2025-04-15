from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64
import logging
import os

PRIVATE_KEY_FILE = "keys/rsu_private_key.pem"
PUBLIC_KEY_FILE = "keys/rsu_public_key.pem"

def generate_rsu_keys():

    if os.path.exists(PRIVATE_KEY_FILE) and os.path.exists(PUBLIC_KEY_FILE):
        logging.info("🔑 RSU keys already exist. Skipping generation.")
        return
    
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()

    # Convert keys to PEM format (Base64 encoded)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Step 2: Convert PEM into RSA key objects
    private_key = serialization.load_pem_private_key(
        private_pem, password=None, backend=default_backend()
    )

    public_key = serialization.load_pem_public_key(
        public_pem, backend=default_backend()
    )

    with open(PRIVATE_KEY_FILE, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open(PUBLIC_KEY_FILE, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    logging.info("✅ RSU Keys successfully obtained and stored.")

    return