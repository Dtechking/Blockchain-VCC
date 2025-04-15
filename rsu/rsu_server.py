import logging
import json
import time
import base64
import threading
from decryptor import decrypt_data
from flask import Flask, jsonify, request
from rsu_key_generator import generate_rsu_keys
from data_aggregator import aggregate_data
from signing import sign_data
from blockchain_integration import send_event_to_blockchain
from data_aggregator import load_cache

# Flask App
app = Flask(__name__)

CONTRACT_DEPLOYED_ADDRESS = "0xcF849cF7bfE724bdfdd13427d9B9F2C2a43acC0a"
EVENT_CACHE_FILE = "cache/events.json"

# Logger Setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Traffic Data Storage
traffic_data_storage = []
data_lock = threading.Lock()  # Thread-safe access

### 📌 2. Background Aggregation Thread
def periodic_aggregation():
    while True:
        time.sleep(15)  # Aggregate data every 15 seconds
        with data_lock:
            if traffic_data_storage:
                logging.info("\n\n🛠️ Aggregating received traffic data...")
                aggregate_data(traffic_data_storage)
                traffic_data_storage.clear()
                logging.info("✅ Aggregation complete. Data cleared.")

# Start Aggregation Thread
threading.Thread(target=periodic_aggregation, daemon=True).start()

### 📌 3. API Endpoint to Receive and Decrypt Data
@app.route("/receive-data", methods=["POST"])
def receive_data():
    try:
        encrypted_data = request.get_json().get("encrypted_data")

        if not encrypted_data:
            raise ValueError("No encrypted data received")

        logging.info("\n\n🔒 Received encrypted data.")

        # Convert JSON string to dictionary
        encrypted_data_dict = json.loads(encrypted_data)

        # Decrypt received data
        logging.info("\n\n🔓 Performing Decryption in RSU...")
        decrypted_data = decrypt_data(encrypted_data_dict)
        logging.info(f"✅ Decrypted Data: {decrypted_data}")

        # Store decrypted data
        with data_lock:
            traffic_data_storage.extend(decrypted_data)
        
        # Process events and send accident-related ones to blockchain
        for event in decrypted_data:
            if event.get("eventType") == "accident":
                # Ensure required fields are present
                required_keys = ["eventId", "eventType", "location", "message", "signature", "vehicle_id"]
                if all(k in event for k in required_keys):
                    # Format location as "lat,lon"
                    loc = event["location"]
                    formatted_location = f"{loc['lat']},{loc['lon']}"

                    # Add properly formatted fields
                    formatted_event = {
                        "eventId": event["eventId"],  # Extract timestamp as numeric ID
                        "eventType": event["eventType"],
                        "location": formatted_location,
                        "message": event["message"],
                        "signature": event["signature"],
                        "vehicle_id": event["vehicle_id"]
                    }

                    # 🧠 Load existing cache or initialize
                    if os.path.exists(EVENT_CACHE_FILE):
                        with open(EVENT_CACHE_FILE, "r") as f:
                            try:
                                cached = json.load(f)
                            except json.JSONDecodeError:
                                cached = {"timestamp": time.time(), "data": {}}
                    else:
                        cached = {"timestamp": time.time(), "data": {}}

                    # 📝 Update cache
                    loc_key = formatted_location
                    if loc_key not in cached["data"]:
                        cached["data"][loc_key] = {
                            "status": "accident",
                            "vehicle_count": 1,
                            "vehicles": [formatted_event]
                        }
                    else:
                        existing = cached["data"][loc_key]
                        # Avoid duplicate vehicle_id entries
                        if not any(v["vehicle_id"] == formatted_event["vehicle_id"] for v in existing["vehicles"]):
                            existing["vehicles"].append(formatted_event)
                            existing["vehicle_count"] = len(existing["vehicles"])

                    cached["timestamp"] = time.time()

                    # 💾 Save updated cache
                    with open(EVENT_CACHE_FILE, "w") as f:
                        json.dump(cached, f, indent=4)

                    # Send to blockchain
                    # TODO: Blockchain Event Sending
                    send_event_to_blockchain(formatted_event)
                else:
                    logging.warning(f"⚠️ Incomplete accident event skipped: {event}")

        return jsonify({"message": "Data received and stored successfully"}), 200

    except Exception as e:
        logging.error(f"❌ Data reception failed: {str(e)}")
        return jsonify({"error": f"Data reception failed: {str(e)}"}), 400

@app.route("/get-rsu-public-key", methods=["GET"])
def get_public_key():
    try:
        # Read the PEM public key file
        with open("keys/rsu_public_key.pem", "rb") as pub_file:
            rsu_public_key = pub_file.read()  # Read as bytes

        # Base64 encode the public key
        encoded_key = base64.b64encode(rsu_public_key).decode('utf-8')

        return jsonify({"rsu_public_key": encoded_key}), 200

    except Exception as e:
        logging.error(f"❌ Data reception failed: {str(e)}")
        return jsonify({"error": f"Data reception failed: {str(e)}"}), 400

@app.route("/broadcast-traffic-alert", methods=["POST"])
def broadcast_traffic_alert():
    try:
        alert_data = request.get_json()

        if not alert_data:
            return jsonify({"error": "Missing alert data"}), 400

        logging.info("📢 Preparing traffic alert for broadcast...")

        # Sign the alert data
        signature = sign_data(alert_data)
        alert_data["signature"] = signature

        # Simulate broadcast (in production, this would be via UDP, MQTT, or some pub-sub)
        logging.info("✅ Alert signed and ready for broadcast.")
        logging.info(json.dumps(alert_data, indent=2))

        # send_event_to_blockchain(alert_data)

        return jsonify({"signed_alert": alert_data}), 200

    except Exception as e:
        logging.error(f"❌ Broadcast failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    generate_rsu_keys()  # Fetch RSU keys before starting the server
    load_cache()
    logging.info("🚀 RSU Flask Server is starting...")
    app.run(host="0.0.0.0", port=5000, debug=True)
