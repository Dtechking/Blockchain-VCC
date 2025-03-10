from flask import Blueprint, request, jsonify
from .validator import validate_data
from .data_aggregator import aggregate_data
import threading

rsu_bp = Blueprint('rsu', __name__)

# Simulated RSU Storage (In-memory for simplicity)
traffic_data_storage = []

@rsu_bp.route('/receive-data', methods=['POST'])
def receive_data():
    data = request.json

    # Validate incoming vehicle data
    is_valid, reason = validate_data(data)
    if not is_valid:
        return jsonify({"error": f"Invalid data: {reason}"}), 400

    # Store the valid data for aggregation
    traffic_data_storage.append(data)

    # Trigger aggregation in a separate thread
    threading.Thread(target=aggregate_data, args=(traffic_data_storage,)).start()

    return jsonify({"message": "Data received successfully"})
