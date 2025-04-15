import hashlib
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

def load_vehicle_private_key_from_pem(pem_path):
    """
    Loads an RSA private key from a PEM file.
    """
    with open(pem_path, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
        return private_key

def sign_vehicle_data(event_id, timestamp, event_type, vehicle_address, location, event_details):
    """
    Creates an RSA signature over the message fields.
    Returns the signature as a hex string.
    """

    VEHICLE_PRIVATE_KEY_PATH = "vehicle_keys/vehicle_private_key.pem"
    private_key = load_vehicle_private_key_from_pem(VEHICLE_PRIVATE_KEY_PATH)

    # Construct the message
    message_string = f"{event_id}|{timestamp}|{event_type}|{vehicle_address}|{location}|{event_details}"
    message_bytes = message_string.encode('utf-8')

    # Sign with RSA using PKCS1v15 and SHA-256
    signature = private_key.sign(
        message_bytes,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    # Return as hex string
    return base64.b64encode(signature).decode('utf-8')
