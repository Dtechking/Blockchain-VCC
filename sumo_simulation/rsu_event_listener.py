import time
import base64
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
import threading

RSU_BROADCAST_ENDPOINT = "http://localhost:5000/broadcast-alerts"
RSU_PUBLIC_KEY_PATH = "rsu_public_key.pem"  # RSU's public key file

# Load RSU public key
def load_rsu_public_key():
    with open(RSU_PUBLIC_KEY_PATH, "rb") as f:
        return serialization.load_pem_public_key(f.read())

# Function to verify RSU broadcasted alerts
def verify_signature(message: str, signature_b64: str) -> bool:
    RSU_PUBLIC_KEY = load_rsu_public_key()
    try:
        RSU_PUBLIC_KEY.verify(
            base64.b64decode(signature_b64),
            message.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False
    except Exception as e:
        print(f"⚠️ Verification error: {e}")
        return False

# Polling thread to receive and verify alerts from RSU
def poll_rsu_broadcasts():
    return
    # while True:
    #     try:
    #         response = requests.get(RSU_BROADCAST_ENDPOINT)
    #         if response.status_code == 200:
    #             alerts = response.json().get("alerts", [])
    #             print(f"\n📡 Received {len(alerts)} broadcast alert(s) from RSU.")

    #             for alert in alerts:
    #                 message = alert.get("message", "")
    #                 signature = alert.get("signature", "")

    #                 if verify_signature(message, signature):
    #                     print(f"✅ Verified alert from RSU: {message}")
    #                 else:
    #                     print(f"❌ Failed to verify alert: {message}")
    #         else:
    #             print(f"⚠️ Failed to fetch alerts: {response.status_code}")
    #     except Exception as e:
    #         print(f"❌ Error fetching RSU broadcasts: {e}")

    #     time.sleep(5)  # poll every 5 seconds
