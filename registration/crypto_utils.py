from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

def generate_keys():
    key = RSA.generate(2048)
    private_key = key.export_key().decode()
    public_key = key.publickey().export_key().decode()
    return private_key, public_key

def sign_data(data, private_key_str):
    private_key = RSA.import_key(private_key_str)
    data_hash = SHA256.new(data.encode('utf-8'))
    signature = pkcs1_15.new(private_key).sign(data_hash)
    return signature.hex()

def verify_signature(data, signature, public_key_str):
    public_key = RSA.import_key(public_key_str)
    data_hash = SHA256.new(data.encode('utf-8'))

    try:
        pkcs1_15.new(public_key).verify(data_hash, bytes.fromhex(signature))
        return True
    except (ValueError, TypeError):
        return False
