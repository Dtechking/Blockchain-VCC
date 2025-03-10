from flask import request, jsonify
from pymongo import MongoClient
from .crypto_utils import generate_keys
import datetime
import os

client = MongoClient("mongodb://localhost:27017/")
db = client['vehicular_cloud']
collection = db['registration']

# Securely store private keys locally on the vehicle side
PRIVATE_KEYS_PATH = "./vehicle_keys/"

if not os.path.exists(PRIVATE_KEYS_PATH):
    os.makedirs(PRIVATE_KEYS_PATH)

def register_entity():
    data = request.json
    entity_id = data.get("entity_id")
    entity_type = data.get("type")

    if not entity_id or not entity_type:
        return jsonify({"error": "Invalid data"}), 400

    private_key, public_key = generate_keys()

    # Store private key securely on the local device
    with open(f"{PRIVATE_KEYS_PATH}{entity_id}_private.pem", "w") as f:
        f.write(private_key)

    registration_data = {
        "entity_id": entity_id,
        "type": entity_type,
        "public_key": public_key,
        "timestamp": datetime.datetime.now().isoformat()
    }

    collection.insert_one(registration_data)
    return jsonify({
        "message": f"{entity_type} registered successfully",
        "public_key": public_key
    })
