import base64
import json
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES

# Load RSU private key
with open("rsu/keys/rsu_private_key.pem", "rb") as priv_file:
    rsu_private_key = RSA.import_key(priv_file.read())

cipher_rsa = PKCS1_OAEP.new(rsu_private_key)

def decrypt_data(encrypted_payload):
    """ Decrypt AES key using RSA, then decrypt the data using AES. """
    
    # Decode Base64 values
    encrypted_aes_key = base64.b64decode(encrypted_payload["aes_key"])
    ciphertext = base64.b64decode(encrypted_payload["ciphertext"])
    nonce = base64.b64decode(encrypted_payload["nonce"])
    tag = base64.b64decode(encrypted_payload["tag"])

    # Decrypt AES key with RSA
    aes_key = cipher_rsa.decrypt(encrypted_aes_key)

    # Decrypt data using AES
    cipher_aes = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
    decrypted_data = cipher_aes.decrypt_and_verify(ciphertext, tag)

    return json.loads(decrypted_data.decode())
