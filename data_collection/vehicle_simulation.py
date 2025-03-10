import threading
import requests
import random
import time
import json
from encryption import encrypt_data  # Encrypts the data

# RSU Endpoint URL
RSU_ENDPOINT = "http://localhost:5000/rsu/receive-data"

# Vehicle IDs for Simulation
VEHICLE_IDS = [f"V-{random.randint(1000, 9999)}" for _ in range(10)]

# Function to simulate vehicle data
def simulate_vehicle(vehicle_id):
    while True:
        # Generate realistic vehicle data
        data = {
            "vehicle_id": vehicle_id,
            "location": {
                "latitude": round(random.uniform(12.90, 12.99), 5),
                "longitude": round(random.uniform(77.50, 77.59), 5)
            },
            "speed": random.randint(0, 100),
            "traffic_status": random.choice(["Congested", "Free-flow", "Accident Detected"]),
            "timestamp": int(time.time())
        }

        # Encrypt data before sending to RSU
        encrypted_data = encrypt_data(data)

        # Send data to RSU
        try:
            response = requests.post(RSU_ENDPOINT, json=encrypted_data)
            if response.status_code == 200:
                print(f"✅ Data from {vehicle_id} sent successfully.")
            else:
                print(f"❗ Failed to send data from {vehicle_id}: {response.json()}")
        except Exception as e:
            print(f"❌ Error sending data from {vehicle_id}: {e}")

        # Simulate real-world movement delay
        time.sleep(random.randint(2, 5))

# Start multiple vehicle simulations using threads
def start_simulation():
    threads = []
    for vehicle_id in VEHICLE_IDS:
        thread = threading.Thread(target=simulate_vehicle, args=(vehicle_id,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    start_simulation()
