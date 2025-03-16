import threading
import time
import json
from flask import Blueprint, request, jsonify
from .data_aggregator import aggregate_data
from .decryption import decrypt_data

rsu_bp = Blueprint('rsu', __name__)

# RSU Data Storage
traffic_data_storage = []
# Lock for thread-safe data access
data_lock = threading.Lock()

# Periodic Aggregation Function
def periodic_aggregation():
    while True:
        time.sleep(15)  # Trigger aggregation every 10 seconds
        
        with data_lock:  # Ensure thread-safe access
            if traffic_data_storage:
                print("\n\nAggregating received data...")
                aggregate_data(traffic_data_storage)
                traffic_data_storage.clear()
                print("✅ Aggregation triggered and data cleared.")

# Start the background thread for aggregation
threading.Thread(target=periodic_aggregation, daemon=True).start()

@rsu_bp.route('/receive-data', methods=['POST'])
def receive_data():
    try:
        encrypted_data = request.json.get("encrypted_data")
        if not encrypted_data:
            raise ValueError("No encrypted data received")

        print("\n\nReceived encrypted data: ")
        print(encrypted_data)

        # 🔹 FIX: Convert JSON string to dictionary
        encrypted_data_dict = json.loads(encrypted_data)

        # Decrypt received data
        print("\n\nPerforming Decryption in RSU: ")
        decrypted_data = decrypt_data(encrypted_data_dict)
        print("Decrypted Data: ")
        print(decrypted_data)

        # Store decrypted data for processing
        with data_lock:
            traffic_data_storage.extend(decrypted_data)

        return jsonify({"message": "Data received and stored successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Data reception failed: {str(e)}"}), 400

    # TODO: Implement Encryption later.
    # try:
    #     encrypted_data = request.json
    #     decrypted_data = decrypt_data(encrypted_data)
        
    #     # Add data to the buffer for aggregation
    #     traffic_data_storage.append(decrypted_data)

    #     return jsonify({"message": "Data received and processed successfully"}), 200
    # except Exception as e:
    #     return jsonify({"error": f"Data reception failed: {str(e)}"}), 400
