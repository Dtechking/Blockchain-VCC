import base64
import json
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.exceptions import InvalidSignature

RSU_PRIVATE_KEY_PATH = "keys/rsu_private_key.pem"

def decrypt_data(encrypted_payload):
    """ Decrypts RSA-encrypted AES key, decrypts AES-GCM data, verifies signature. """

    # Step 1: Decode all Base64-encoded fields
    encrypted_aes_key = base64.b64decode(encrypted_payload["aes_key"])
    ciphertext = base64.b64decode(encrypted_payload["ciphertext"])
    nonce = base64.b64decode(encrypted_payload["nonce"])
    tag = base64.b64decode(encrypted_payload["tag"])

    # Step 2: Load RSU private RSA key
    with open(RSU_PRIVATE_KEY_PATH, "rb") as priv_file:
        rsu_private_key = RSA.import_key(priv_file.read())

    cipher_rsa = PKCS1_OAEP.new(rsu_private_key)

    # Step 3: Decrypt AES key using RSA
    aes_key = cipher_rsa.decrypt(encrypted_aes_key)

    # Step 4: Decrypt ciphertext using AES-GCM
    cipher_aes = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
    decrypted_signed_package_bytes = cipher_aes.decrypt_and_verify(ciphertext, tag)
    signed_package = json.loads(decrypted_signed_package_bytes.decode())

    # Step 5: Extract original components
    payload_b64 = signed_package["payload"]
    signature_b64 = signed_package["signature"]
    vehicle_public_key_b64 = signed_package["vehicle_public_key"]

    payload = base64.b64decode(payload_b64)
    signature = base64.b64decode(signature_b64)
    vehicle_public_key_pem = base64.b64decode(vehicle_public_key_b64)

    # Step 6: Load vehicle public key (PEM) and verify signature
    vehicle_public_key = serialization.load_pem_public_key(vehicle_public_key_pem)

    try:
        vehicle_public_key.verify(
            signature,
            payload,
            asym_padding.PSS(
                mgf=asym_padding.MGF1(hashes.SHA256()),
                salt_length=asym_padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
    except InvalidSignature:
        raise ValueError("❌ Signature verification failed. Data may be tampered.")

    # Step 7: Return the original payload (verified and trusted)
    return json.loads(payload.decode())
