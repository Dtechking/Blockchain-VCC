from web3 import Web3
import json
import logging
import base64
import os

# Get the absolute path to the file
file_path = os.path.join(os.path.dirname(__file__), 'contract_details', 'TrafficEventLogger.json')


# Connect to local Ganache
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
assert web3.is_connected(), "❌ Unable to connect to Ganache"

# Load contract ABI and address
CONTRACT_DEPLOYED_ADDRESS = "0x76cA49e2eE33aeE35fc38EAf3f0F0E70c15dB8ef"

with open(file_path) as f:
    contract_json = json.load(f)
    abi = contract_json["abi"]
    contract_address = CONTRACT_DEPLOYED_ADDRESS

# Set your deployed contract address here
contract = web3.eth.contract(address=contract_address, abi=abi)

# RSU's account details
rsu_address = "0xB5E9B642EE03577FBE341306aFC583130304c35a"
rsu_private_key = "0x791245bb39bed4771a0a53c1cd1bb5102b4969d9676e8e5d7e8d29eba65c1ac0"

# Function to send event to blockchain
def send_event_to_blockchain(event_data):
    try:
        logging.info("🛠️ Sending event data to blockchain...")

        # Extract data
        event_id = event_data["eventId"]
        timestamp = str(event_data["timestamp"])
        event_type = event_data["eventType"]
        event_hash = web3.keccak(text=event_data["message"])  # Assuming message is used to create hash
        location = event_data["location"]
        event_details = event_data["message"]
        vehicle_id = event_data["vehicle_id"]
        signature = base64.b64decode(event_data["signature"])  # Signature must be bytes

        assert isinstance(event_id, str)
        assert isinstance(timestamp, str)
        assert isinstance(event_type, str)
        assert isinstance(event_hash, bytes)
        assert len(event_hash) == 32

        assert isinstance(vehicle_id, str)
        assert isinstance(location, str)
        assert isinstance(event_details, str)
        assert isinstance(signature, bytes)

        # logging.info(f"Signature Length: {len(signature)}")
        # assert len(signature) == 65

        # Dry run simulation (optional, but useful)
        # try:
        #     contract.functions.logAlert(
        #         event_id, event_type, event_hash, vehicle_id,
        #         location, event_details, signature
        #     ).call({'from': rsu_address})
        #     print("✅ Dry run successful.")
        # except Exception as dry_run_error:
        #     logging.error(f"⚠️ Dry run failed: {dry_run_error}")
        #     raise dry_run_error

        # Build transaction
        txn = contract.functions.logAlert(
            event_id,
            timestamp,
            event_type,
            event_hash,
            vehicle_id,
            location,
            event_details,
            signature
        ).build_transaction({
            'from': rsu_address,
            'nonce': web3.eth.get_transaction_count(rsu_address),
            'gas': 500000,  # increased gas
            'gasPrice': web3.to_wei('10', 'gwei')
        })

        logging.info("🖋️ Signing transaction...")
        signed_txn = web3.eth.account.sign_transaction(txn, private_key=rsu_private_key)

        logging.info("🚀 Sending transaction to blockchain...")
        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)

        logging.info("⏳ Waiting for transaction receipt...")
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        logging.info(f"✅ Event successfully logged! Tx Hash: {tx_hash.hex()}")
        return tx_hash.hex()

    except Exception as e:
        logging.error(f"❌ Error sending event to blockchain: {str(e)}")
        return None
    
def get_event_by_id(event_id: str):
    try:
        event_data = contract.functions.getEventDetails(event_id).call()
        # print(f"Event data received by RSU : {event_data}")
        print(f"Signature (Base64): {base64.b64encode(event_data[7]).decode()}")
        # Unpack struct
        return {
            "eventId": event_data[0],
            "timestamp": event_data[1],
            "eventType": event_data[2],
            "eventHash": event_data[3],
            "vehicle_id": event_data[4],
            "location": event_data[5],
            "message": event_data[6],  # eventDetails
            "signature": base64.b64encode(event_data[7]).decode()  # Convert bytes to base64 string
        }
    except Exception as e:
        logging.error(f"❌ Failed to fetch event by ID: {e}")
        return None