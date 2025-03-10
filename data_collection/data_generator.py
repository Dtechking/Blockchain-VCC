import random
import json
import time

# Function to generate realistic vehicle data
def generate_vehicle_data(vehicle_id=None):
    # Generate a random vehicle ID if none is provided
    vehicle_id = vehicle_id or f"V-{random.randint(1000, 9999)}"
    
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
    
    return json.dumps(data)

# Test the function independently
if __name__ == "__main__":
    for _ in range(5):
        print(generate_vehicle_data())
        time.sleep(1)  # Simulate real-time data intervals
