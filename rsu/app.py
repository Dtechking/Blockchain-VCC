import logging
import json
import time
import base64
import threading
from decryption import decrypt_data
from flask import Flask, jsonify, request
from rsu_data_receiver import fetch_rsu_keys
from data_aggregator import aggregate_data

# Flask App
app = Flask(__name__)

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

if __name__ == "__main__":
    fetch_rsu_keys()  # Fetch RSU keys before starting the server
    logging.info("🚀 RSU Flask Server is starting...")
    app.run(host="0.0.0.0", port=5000, debug=True)
