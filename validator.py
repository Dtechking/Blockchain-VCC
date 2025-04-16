import base64
import requests
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

from rsu.blockchain_integration import get_event_by_id

# Replace with actual key fetch logic (e.g., DB or key server)
def get_vehicle_public_key() -> str:
    url = "http://localhost:5002/get-vehicle-public-key"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            public_key_b64 = data["vehicle_public_key"]
            # print(f"[PUBLIC KEY] base64: {public_key_b64}")
            public_key_bytes = base64.b64decode(public_key_b64)
            # print(f"[PUBLIC KEY] PEM decoded:\n{public_key_bytes.decode()}")
            return public_key_bytes
        else:
            print(f"Failed to get vehicle public key: {response.status_code}")
    except Exception as e:
        print(f"Error fetching vehicle public key: {e}")
    return None


def validate_event_signature(event_id: str) -> bool:
    try:
        event = get_event_by_id(event_id)
        if not event:
            print("❌ Event not found on blockchain.")
            return False
        
        timestamp = event["timestamp"]
        event_type = event["eventType"]
        vehicle_address = event["vehicle_id"]
        location = event["location"]
        event_details = event["message"]

        signature = base64.b64decode(event["signature"])
        print(f"\n\n[VERIFY] Signature (base64): {event["signature"]}")

        message_string = f"{event_id}|{timestamp}|{event_type}|{vehicle_address}|{location}|{event_details}"
        message_bytes = message_string.encode('utf-8')

        print(f"\n\n[VERIFY] Message: {message_string}")
        # print(f"[VERIFY] Message Bytes: {message_bytes}")

        public_key_pem = get_vehicle_public_key()
        if not public_key_pem:
            print(f"❌ Public key for vehicle '{vehicle_address}' not found.")
            return False

        public_key = serialization.load_pem_public_key(public_key_pem)
        # print(f"[VERIFY] Public key loaded: {public_key}")

        public_key.verify(
            signature,
            message_bytes,
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        print("\n\n✅ Signature is valid.")
        return True

    except Exception as e:
        print(f"❌ Signature validation failed: {e}")
        return False

if __name__ == "__main__":
    # Ask for the event ID when running the script
    event_id = input("Please enter the event ID to verify the signature: ")
    validate_event_signature(event_id)