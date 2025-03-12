from flask import Flask, jsonify, request
from registration.registration import register_entity
from data_collection.data_generator import generate_vehicle_data
# from blockchain.contract_interaction import store_data_on_blockchain
from rsu import rsu_bp
import logging
import threading
from data_collection.vehicle_simulation import start_simulation
import signal
import sys

# Initialize Flask app
app = Flask(__name__)

# Configure logging for better tracking
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Register RSU Blueprint
app.register_blueprint(rsu_bp, url_prefix='/rsu')

# Graceful shutdown handler
def shutdown_server(signal_received, frame):
    logging.info("Shutdown signal received. Stopping vehicle simulation and server.")
    sys.exit(0)

# Register the shutdown signal
signal.signal(signal.SIGINT, shutdown_server)
signal.signal(signal.SIGTERM, shutdown_server)

# Start the vehicle data simulation in a separate thread
def run_simulation():
    threading.Thread(target=start_simulation, daemon=True).start()

# Vehicle Registration Endpoint
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        if not data:
            raise ValueError("No registration data provided")
        
        response = register_entity(data)
        logging.info(f"Vehicle Registered Successfully: {data}")
        return jsonify({"message": "Vehicle registered successfully", "details": response}), 201
    except ValueError as ve:
        logging.warning(f"Vehicle Registration Warning: {str(ve)}")
        return jsonify({"warning": str(ve)}), 400
    except Exception as e:
        logging.error(f"Vehicle Registration Failed: {str(e)}")
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500

# Data Generation and Encryption Endpoint
@app.route('/simulate-data', methods=['POST'])
def simulate_data():
    try:
        simulated_data = generate_vehicle_data()
        logging.info(f"Data Simulated Successfully: {simulated_data}")
        return jsonify({"message": "Vehicle data simulated successfully", "data": simulated_data}), 200
    except Exception as e:
        logging.error(f"Data Simulation Failed: {str(e)}")
        return jsonify({"error": f"Data simulation failed: {str(e)}"}), 500

# Blockchain Data Storage Endpoint
@app.route('/store-data', methods=['POST'])
def store_data():
    try:
        data = request.json
        if not data:
            raise ValueError("No data provided for blockchain storage")

        # response = store_data_on_blockchain(data)
        logging.info(f"Data Stored on Blockchain Successfully: {data}")
        return jsonify({"message": "Data stored successfully", "transaction": response}), 201
    except ValueError as ve:
        logging.warning(f"Blockchain Data Warning: {str(ve)}")
        return jsonify({"warning": str(ve)}), 400
    except Exception as e:
        logging.error(f"Blockchain Data Storage Failed: {str(e)}")
        return jsonify({"error": f"Blockchain data storage failed: {str(e)}"}), 500

# Default route to ensure server is running
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "Server is running"}), 200

# Main driver function
if __name__ == '__main__':
    try:
        # run_simulation()
        app.run(debug=True, port=5000)
    except Exception as e:
        logging.critical(f"Server startup failed: {str(e)}")
