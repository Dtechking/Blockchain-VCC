import traci
import requests
import json
import random
import time

RSU_ENDPOINT = "http://localhost:5000/rsu/receive-data"

def send_vehicle_data(vehicle_id, location, speed, traffic_status):
    data = {
        "vehicle_id": vehicle_id,
        "location": location,
        "speed": speed,
        "traffic_status": traffic_status,
        "timestamp": int(time.time())
    }

    try:
        response = requests.post(RSU_ENDPOINT, json=data)
        if response.status_code == 200:
            print(f"✅ Data from {vehicle_id} sent successfully.")
        else:
            print(f"❗ Failed to send data from {vehicle_id}: {response.json()}")
    except Exception as e:
        print(f"❌ Error sending data from {vehicle_id}: {e}")

def run_sumo():
    traci.start(["sumo", "-n", "network.net.xml", "-r", "routes.rou.xml"])

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        # Extract vehicle data
        for vehicle_id in traci.vehicle.getIDList():
            position = traci.vehicle.getPosition(vehicle_id)
            speed = traci.vehicle.getSpeed(vehicle_id)

            location = {"latitude": position[0], "longitude": position[1]}
            traffic_status = random.choice(["Congested", "Free-flow", "Accident Detected"])

            # Send data to RSU API
            send_vehicle_data(vehicle_id, location, speed, traffic_status)

        time.sleep(1)  # Control simulation speed

    traci.close()

if __name__ == "__main__":
    run_sumo()
