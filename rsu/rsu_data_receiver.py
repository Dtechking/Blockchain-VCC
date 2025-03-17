import os
import json
import time
import threading
import logging
import requests
import base64
from flask import Blueprint, request, jsonify
from Crypto.PublicKey import RSA
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from decryption import decrypt_data


# Configuration
KEY_GENERATOR_URL = "http://localhost:5001/generate-keys"
KEYS_FOLDER = "keys"
PRIVATE_KEY_FILE = os.path.join(KEYS_FOLDER, "rsu_private_key.pem")
PUBLIC_KEY_FILE = os.path.join(KEYS_FOLDER, "rsu_public_key.pem")
API_KEY = "get_secure_rsa_keys"

# Logger Setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


### 📌 1. Fetch RSU Keys from Key Generator on Startup
def fetch_rsu_keys():
    try:

        if os.path.exists(PRIVATE_KEY_FILE) and os.path.exists(PUBLIC_KEY_FILE):
            logging.info("✅ RSU Keys already exist. Skipping fetch.")
            return
        
        logging.info("🔄 Requesting RSU keys from Key Generator Module...")
        
        # Send request with authentication header
        headers = {"X-API-KEY": API_KEY}
        response = requests.get(KEY_GENERATOR_URL, headers=headers)

        if response.status_code == 200:
            keys = response.json()
            private_key_b64 = keys.get("private_key")
            public_key_b64 = keys.get("public_key")

            if private_key_b64 and public_key_b64:
                os.makedirs(KEYS_FOLDER, exist_ok=True)

                # Step 1: Decode Base64 to get original PEM
                private_pem = base64.b64decode(private_key_b64)
                public_pem = base64.b64decode(public_key_b64)

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
            else:
                logging.error("❗ Invalid keys received from Key Generator Module.")
        else:
            logging.error(f"❌ Failed to fetch RSU Keys: {response.text}")

    except Exception as e:
        logging.error(f"❌ Error fetching RSU Keys: {e}")