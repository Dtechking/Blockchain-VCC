import traci
import requests
import json
import random
import time
import os
import base64
from encryptor import encrypt_data
from rsu_event_listener import poll_rsu_broadcasts
from sign_vehicle_data import sign_vehicle_data
import threading


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "map.sumocfg")

RSU_ENDPOINT = "http://localhost:5000/receive-data"

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
                try:
                    response_json = response.json()
                    print(f"✅ Data batch sent successfully: {response_json}")
                except json.JSONDecodeError:
                    print(f"⚠️ Error: RSU response is not valid JSON: {response.text}")
            else:
                print(f"❗ Failed to send data batch: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error sending data batch: {e}")
        
        # Clear buffer after sending
        vehicle_data_buffer.clear()
        LAST_SEND_TIME = time.time()

def run_sumo():
    global LAST_SEND_TIME
    event_counter = 0  # For unique event IDs

    threading.Thread(target=poll_rsu_broadcasts, daemon=True).start()
    traci.start(["sumo-gui", "-c", CONFIG_PATH])

    print("\n\nSumo Simulation Started, Getting Vehicle data:")
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        time.sleep(0.5)

        # Extract vehicle data
        for vehicle_id in traci.vehicle.getIDList():
            position = traci.vehicle.getPosition(vehicle_id)
            speed = traci.vehicle.getSpeed(vehicle_id)
            event_type = ""
            message = ""
            event_id = None

            # Normalize location to grid for easier tracking
            lat = int(position[0] // 250)
            lon = int(position[1] // 250)
            location = {"lat": lat, "lon": lon}

            traffic_status = random.choices(
                ["Congested", "Free-flow", "Moderate"],
                weights=[0.1, 0.75, 0.15]
            )[0]

            # Simulated Accident Location
            if lat == -1 and lon == 0:
                traffic_status = "Congested"
                event_type = "accident"
                message = f"Accident reported by {vehicle_id} at location ({lat}, {lon})"
                event_id = f"{vehicle_id}_{int(time.time())}"  # unique ID using vehicle + time

            timestamp = int(time.time())
            # Prepare data packet
            vehicle_data_buffer[vehicle_id] = {
                "vehicle_id": vehicle_id,
                "location": location,
                "speed": speed,
                "traffic_status": traffic_status,
                "timestamp": timestamp,
                "eventType": event_type,
                "message": message,
                "eventId": event_id
            }

            vehicle_data_buffer[vehicle_id]["signature"] = sign_vehicle_data(
                event_id,
                f"{timestamp}",
                event_type,
                vehicle_id,
                f"{location['lat']},{location['lon']}",
                message
            )

            print(vehicle_data_buffer[vehicle_id])

        # Send batched data every 10 seconds
        if time.time() - LAST_SEND_TIME >= SEND_INTERVAL:
            send_vehicle_data()

    print("✅ SUMO Simulation Completed. Keeping GUI open.")
    input("Press Enter to exit SUMO...")  # Keeps SUMO open until user presses Enter
    traci.close()
