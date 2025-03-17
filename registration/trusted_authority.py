import logging
from flask import Flask, jsonify, request
from key_generator import generate_keys

API_KEY = "get_secure_rsa_keys"


app = Flask(__name__)


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

@app.route('/generate-keys', methods=['GET'])
def generate_keys_api():
    """Securely generates and returns encrypted RSA keys"""
    
    logging.info("Received request for RSA key generation")

    # Authenticate request
    if request.headers.get("X-API-KEY") != API_KEY:
        logging.warning("Unauthorized access attempt detected")
        return jsonify({"error": "Unauthorized"}), 401

    logging.info("Authentication successful, generating keys...")
    
    try:
        private_key, public_key = generate_keys()
        logging.info("🔑 RSA keys generated successfully")

        return jsonify({
            "private_key": private_key,
            "public_key": public_key
        }), 200
    except Exception as e:
        logging.error(f"Error generating RSA keys: {str(e)}")
        return jsonify({"error": "Key generation failed"}), 500

if __name__ == '__main__':
    logging.info("🚀 Trusted Authority Server is starting on port 5001...")
    app.run(port=5001, debug=True)