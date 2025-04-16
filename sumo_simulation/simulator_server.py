import requests
import threading
import logging
import time
import base64
import os
from simulator import run_sumo  # Import the simulation function
from encryptor import encrypt_data
from flask import Flask, jsonify, request
from vehicle_key_generator import generate_vehicle_keys

# RSU server endpoint
RSU_PUBLIC_KEY_URL = "http://localhost:5000/get-rsu-public-key"
RSU_KEY_FILE = "rsu_key/rsu_public_key.pem"

# Flask app initialization
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Store the RSU public key
rsu_public_key = None

# Function to fetch the RSU public key with retries
def get_rsu_public_key(retries=3, delay=3):
    global rsu_public_key

    # Check if the key file already exists
    if os.path.exists(RSU_KEY_FILE):
        logging.info(f"✅ RSU Public Key already exists at {RSU_KEY_FILE}. Skipping fetch.")
        return
    
    for attempt in range(retries):
        try:
            logging.info(f"🔄 Attempt {attempt + 1}: Fetching RSU Public Key...")
            response = requests.get(RSU_PUBLIC_KEY_URL, timeout=5)
            
            if response.status_code == 200:
                json_data = response.json()
                if "rsu_public_key" in json_data:
                    rsu_public_key = json_data["rsu_public_key"]
                    
                    # Decode the public key
                    decoded_key = base64.b64decode(rsu_public_key)

                    # Save the decoded key as a PEM file (optional)
                    with open("rsu_key/rsu_public_key.pem", "wb") as pem_file:
                        pem_file.write(decoded_key)

                    logging.info(f"✅ RSU Public Key obtained and saved to {RSU_KEY_FILE}")
                    return  # Exit loop if successful
                else:
                    logging.warning(f"⚠️ RSU response missing 'public_key' key: {json_data}")
            else:
                logging.warning(f"❗ Failed to fetch RSU Public Key: {response.status_code} - {response.text}")

        except requests.RequestException as e:
            logging.error(f"❌ Error fetching RSU Public Key: {e}")

        time.sleep(delay)  # Wait before retrying

    logging.error("🚨 All retries failed: Unable to fetch RSU Public Key.")


# Route to manually request RSU public key
@app.route('/get-rsu-key', methods=['GET'])
def fetch_rsu_key():
    get_rsu_public_key()
    if rsu_public_key:
        return jsonify({"public_key": rsu_public_key}), 200
    return jsonify({"error": "Failed to retrieve RSU public key"}), 500


# Start SUMO simulation when requested
@app.route('/start-simulation', methods=['POST'])
def start_simulation():
    try:
        # Start SUMO in a separate thread
        thread = threading.Thread(target=run_sumo, daemon=True)
        thread.start()
        return jsonify({"message": "SUMO Simulation started"}), 200
    except Exception as e:
        logging.error(f"❌ Error starting SUMO simulation: {e}")
        return jsonify({"error": str(e)}), 500
    
# New route to expose vehicle's RSA public key
@app.route('/get-vehicle-public-key', methods=['GET'])
def get_vehicle_public_key():
    try:
        with open("vehicle_keys/vehicle_public_key.pem", "rb") as f:
            public_key_bytes = f.read()
            encoded_key = base64.b64encode(public_key_bytes).decode("utf-8")
            return jsonify({"vehicle_public_key": encoded_key}), 200
    except FileNotFoundError:
        logging.error("🚫 Vehicle public key file not found.")
        return jsonify({"error": "Vehicle public key not found"}), 404
    except Exception as e:
        logging.error(f"❌ Error reading vehicle public key: {e}")
        return jsonify({"error": "Failed to load vehicle public key"}), 500



# Health check route
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "SUMO Simulator Server is running"}), 200


# Main driver function
if __name__ == '__main__':
    generate_vehicle_keys()
    get_rsu_public_key()  # Fetch RSU key on startup
    logging.info("🚀 SUMO Simulator Server is starting...")

    # Run SUMO simulator in a background thread
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        sumo_thread = threading.Thread(target=run_sumo)
        sumo_thread.start()

    # Run Flask server in main thread (reloader works fine here)
    app.run(debug=True, port=5002)