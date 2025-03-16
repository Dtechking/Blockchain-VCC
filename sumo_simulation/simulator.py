import traci
import requests
import json
import random
import time
import os
import base64
from encryption import encrypt_data

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "map.sumocfg")

RSU_ENDPOINT = "http://localhost:5000/rsu/receive-data"

# Buffer for batched data
vehicle_data_buffer = {}
LAST_SEND_TIME = 0
SEND_INTERVAL = 3  # Send data every 10 seconds

def send_vehicle_data():
    global LAST_SEND_TIME
    if vehicle_data_buffer:
        try:
            print("\n\nPerforming Encryption before sending to RSU...")
            encrypted_payload = encrypt_data(list(vehicle_data_buffer.values()))
            print("Encrypted Data: ")
            print(encrypted_payload)
            response = requests.post(RSU_ENDPOINT, json={"encrypted_data": encrypted_payload})

            if response.status_code == 200:
                print(f"✅ Data batch sent successfully.")
            else:
                print(f"❗ Failed to send data batch: {response.json()}")
        except Exception as e:
            print(f"❌ Error sending data batch: {e}")
        
        # Clear buffer after sending
        vehicle_data_buffer.clear()
        LAST_SEND_TIME = time.time()

def run_sumo():
    global LAST_SEND_TIME

    traci.start(["sumo-gui", "-c", CONFIG_PATH])

    print("\n\nSumo Simulation Started, Getting Vehicle data:")
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        time.sleep(0.5)

        # Extract vehicle data
        for vehicle_id in traci.vehicle.getIDList():
            position = traci.vehicle.getPosition(vehicle_id)
            speed = traci.vehicle.getSpeed(vehicle_id)

            location = {"latitude": int(position[0] // 250), "longitude": int(position[1] // 250)}
            traffic_status = random.choices(
                ["Congested", "Free-flow"],
                weights=[0.2, 0.8]
            )[0]

            # Specifying a Accident Location
            if location["latitude"] == -1 and location["longitude"] == 0:
                traffic_status = "Accident"
                

            # Store vehicle data in buffer
            vehicle_data_buffer[vehicle_id] = {
                "vehicle_id": vehicle_id,
                "location": location,
                "speed": speed,
                "traffic_status": traffic_status,
                "timestamp": int(time.time())
            }

            print(vehicle_data_buffer[vehicle_id])

        # Send batched data every 10 seconds
        if time.time() - LAST_SEND_TIME >= SEND_INTERVAL:
            send_vehicle_data()

    print("✅ SUMO Simulation Completed. Keeping GUI open.")
    input("Press Enter to exit SUMO...")  # Keeps SUMO open until user presses Enter
    traci.close()

if __name__ == "__main__":
    run_sumo()
