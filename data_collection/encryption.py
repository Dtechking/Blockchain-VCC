from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import json

# AES-256 Encryption Key (For Testing)
SECRET_KEY = b'1234567890abcdef1234567890abcdef'

# Encrypt data with AES-256
def encrypt_data(data):
    cipher = AES.new(SECRET_KEY, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(json.dumps(data).encode('utf-8'))
    
    return {
        "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
        "nonce": base64.b64encode(cipher.nonce).decode('utf-8'),
        "tag": base64.b64encode(tag).decode('utf-8')
    }

# Decrypt data (For Testing or RSU Validation)
def decrypt_data(encrypted_data):
    cipher = AES.new(SECRET_KEY, AES.MODE_GCM, nonce=base64.b64decode(encrypted_data['nonce']))
    decrypted_data = cipher.decrypt_and_verify(
        base64.b64decode(encrypted_data['ciphertext']),
        base64.b64decode(encrypted_data['tag'])
    )
    return json.loads(decrypted_data.decode('utf-8'))
