import os
import logging
import base64
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.x509.oid import NameOID
from flask import Flask, jsonify, request
from datetime import datetime, timedelta, timezone

# Configure logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class CertificateAuthority:
    def __init__(self, cert_file, key_file):
        self.cert_file = cert_file
        self.key_file = key_file
        self.private_key = None
        self.public_key = None
        self.load_or_generate_keys()

    def load_or_generate_keys(self):
        if os.path.exists(self.key_file) and os.path.exists(self.cert_file):
            # Load existing private key and certificate
            with open(self.key_file, "rb") as key_file:
                self.private_key = serialization.load_pem_private_key(key_file.read(), password=None)
            with open(self.cert_file, "rb") as cert_file:
                self.public_key = x509.load_pem_x509_certificate(cert_file.read())
        else:
            # Generate new keys and self-signed certificate
            self.generate_keys_and_certificate()

    def generate_keys_and_certificate(self):
        # Generate private key
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        with open(self.key_file, "wb") as key_file:
            key_file.write(private_pem)

        # Generate public key
        public_key = self.private_key.public_key()

        # Create self-signed certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"IN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Tamilnadu"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, u"Chennai"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"RSU CA"),
            x509.NameAttribute(NameOID.COMMON_NAME, u"RSU Certificate Authority"),
        ])

        certificate = x509.CertificateBuilder().subject_name(subject).issuer_name(issuer).public_key(public_key).serial_number(x509.random_serial_number()).not_valid_before(datetime.now(timezone.utc)).not_valid_after(datetime.now(timezone.utc) + timedelta(days=3650)).add_extension(x509.SubjectAlternativeName([x509.DNSName(u"localhost")]), critical=False).sign(self.private_key, hashes.SHA256())

        with open(self.cert_file, "wb") as cert_file:
            cert_file.write(certificate.public_bytes(encoding=serialization.Encoding.PEM))

        self.public_key = certificate

    def sign_certificate(self, cert_data):
        """ Sign the certificate data with the private key of the CA. """
        certificate = x509.CertificateBuilder().subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cert_data['subject'])])).issuer_name(self.public_key.subject).public_key(cert_data['public_key']).serial_number(x509.random_serial_number()).not_valid_before(datetime.now(timezone.utc)).not_valid_after(datetime.now(timezone.utc) + timedelta(days=3650)).sign(self.private_key, hashes.SHA256())

        return certificate.public_bytes(encoding=serialization.Encoding.PEM)

    def verify_certificate(self, cert_pem):
        """ Verify the provided certificate using the CA public key. """
        certificate = x509.load_pem_x509_certificate(cert_pem)
        public_key = self.public_key.public_key()

        try:
            public_key.verify(certificate.signature, certificate.tbs_certificate_bytes, padding.PKCS1v15(), hashes.SHA256())
            logging.info("✅ Certificate successfully verified.")
            return True
        except Exception as e:
            logging.error(f"❌ Certificate verification failed: {e}")
            return False


# Flask API to interact with the Certificate Authority
app = Flask(__name__)

# Create a global instance of the CertificateAuthority
ca = CertificateAuthority(cert_file="keys/ca_certificate.pem", key_file="keys/ca_private_key.pem")

@app.route('/get-certificate', methods=['POST'])
def get_certificate():
    """ API to generate a signed certificate for an entity. """
    try:
        data = request.get_json()
        subject = data.get('subject')
        public_key_pem = base64.b64decode(data.get('public_key'))

        # Generate the certificate
        public_key = serialization.load_pem_public_key(public_key_pem)
        cert_data = {
            'subject': subject,
            'public_key': public_key
        }

        signed_certificate = ca.sign_certificate(cert_data)
        logging.info(f"📜 Signed Certificate PEM:\n{signed_certificate.decode()}")

        return jsonify({"signed_certificate": base64.b64encode(signed_certificate).decode('utf-8')}), 200
    except Exception as e:
        logging.error(f"❌ Error generating certificate: {e}")
        return jsonify({"error": "Error generating certificate"}), 500

@app.route('/verify-certificate', methods=['POST'])
def verify_certificate():
    """ API to verify the certificate signature. """
    try:
        data = request.get_json()
        encoded_cert = data.get('certificate')
        logging.info(f"🧾 Base64 Encoded Cert Received:\n{encoded_cert[:300]}")
        certificate_pem = base64.b64decode(encoded_cert)
        logging.info(f"📄 Decoded Cert PEM (first 300 chars):\n{certificate_pem[:300]}")

        # Verify the certificate
        is_valid = ca.verify_certificate(certificate_pem)

        if is_valid:
            return jsonify({"message": "Certificate is valid"}), 200
        else:
            return jsonify({"message": "Certificate is invalid"}), 400
    except Exception as e:
        logging.error(f"❌ Error verifying certificate: {e}")
        return jsonify({"error": "Error verifying certificate"}), 500

if __name__ == "__main__":
    logging.info("🚀 Certificate Authority Server is starting...")
    app.run(host="0.0.0.0", port=5001, debug=True)
