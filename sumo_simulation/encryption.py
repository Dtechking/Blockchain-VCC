from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
import base64
import json

# Load RSU public key
with open("rsu_public_key.pem", "rb") as pub_file:
    rsu_public_key = RSA.import_key(pub_file.read())

cipher_rsa = PKCS1_OAEP.new(rsu_public_key)

def encrypt_data(data):
    """ Encrypt data using AES, then encrypt the AES key using RSA. """
    
    # Convert data to JSON string
    json_data = json.dumps(data).encode()

    # Generate AES key and IV
    aes_key = get_random_bytes(16)  # 16-byte AES key
    cipher_aes = AES.new(aes_key, AES.MODE_GCM)
    ciphertext, tag = cipher_aes.encrypt_and_digest(json_data)

    # Encrypt AES key using RSA
    cipher_rsa = PKCS1_OAEP.new(rsu_public_key)
    encrypted_aes_key = cipher_rsa.encrypt(aes_key)

    # Return encrypted AES key + encrypted data
    return json.dumps({
        "aes_key": base64.b64encode(encrypted_aes_key).decode(),  # RSA-encrypted AES key
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "nonce": base64.b64encode(cipher_aes.nonce).decode(),
        "tag": base64.b64encode(tag).decode()
    })