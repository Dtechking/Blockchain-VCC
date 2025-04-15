# sumo_simulation/encryptor.py

import base64
import json
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend

VEHICLE_PRIVATE_KEY_PATH = "vehicle_keys/vehicle_private_key.pem"
VEHICLE_PUBLIC_KEY_PATH = "vehicle_keys/vehicle_public_key.pem"
RSU_PUBLIC_KEY_PATH = "rsu_key/rsu_public_key.pem"

def load_private_key(path):
    with open(path, "rb") as key_file:
        return serialization.load_pem_private_key(key_file.read(), password=None, backend=default_backend())

def load_public_key(path):
    with open(path, "rb") as key_file:
        return serialization.load_pem_public_key(key_file.read(), backend=default_backend())

def encrypt_data(data):
    # 1. Load keys
    vehicle_private_key = load_private_key(VEHICLE_PRIVATE_KEY_PATH)
    vehicle_public_key = load_public_key(VEHICLE_PUBLIC_KEY_PATH)

    with open(RSU_PUBLIC_KEY_PATH, "rb") as f:
        rsu_public_key_rsa = RSA.import_key(f.read())  # Use PyCryptodome RSA key for encryption

    # 2. Serialize the data
    payload_json = json.dumps(data).encode()

    # 3. Sign the payload
    signature = vehicle_private_key.sign(
        payload_json,
        asym_padding.PSS(
            mgf=asym_padding.MGF1(hashes.SHA256()),
            salt_length=asym_padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    # 4. Get vehicle public key (in PEM format)
    vehicle_public_pem = vehicle_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # 5. Create the signed package
    signed_package = {
        "payload": base64.b64encode(payload_json).decode(),
        "signature": base64.b64encode(signature).decode(),
        "vehicle_public_key": base64.b64encode(vehicle_public_pem).decode()
    }

    # 6. Encrypt signed package using AES
    aes_key = get_random_bytes(16)
    cipher_aes = AES.new(aes_key, AES.MODE_GCM)
    signed_package_bytes = json.dumps(signed_package).encode()
    ciphertext, tag = cipher_aes.encrypt_and_digest(signed_package_bytes)

    # 7. Encrypt AES key with RSU's RSA public key
    cipher_rsa = PKCS1_OAEP.new(rsu_public_key_rsa)
    encrypted_aes_key = cipher_rsa.encrypt(aes_key)

    # 8. Return everything in Base64-encoded JSON format
    return json.dumps({
        "aes_key": base64.b64encode(encrypted_aes_key).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "nonce": base64.b64encode(cipher_aes.nonce).decode(),
        "tag": base64.b64encode(tag).decode()
    })
