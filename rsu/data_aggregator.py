from collections import defaultdict
import time

# Aggregated data structure
aggregated_data = defaultdict(lambda: {
    "status": None,
    "vehicle_count": 0,
    "vehicles": []  # List of {"vehicle_id", "timestamp"}
})

traffic_data = []

# Add data to aggregation
def aggregate_data(traffic_data_storage):
    current_time = time.time()

    # Clear outdated entries before aggregation
    # clear_old_data(current_time)

    for vehicle_data in traffic_data_storage:
        location = tuple(vehicle_data["location"].values())  # Convert to tuple for key
        vehicle_id = vehicle_data["vehicle_id"]
        timestamp = vehicle_data["timestamp"]
        status = vehicle_data["traffic_status"]

        # Initialize aggregation entry if new location
        if not aggregated_data[location]["status"]:
            aggregated_data[location]["status"] = status

        # Check for existing vehicle and update its timestamp
        for vehicle in aggregated_data[location]["vehicles"]:
            if vehicle["vehicle_id"] == vehicle_id:
                vehicle["timestamp"] = max(vehicle["timestamp"], timestamp)  # Update with latest timestamp
                break
        else:
            # Add new vehicle entry if not found
            aggregated_data[location]["vehicles"].append({"vehicle_id": vehicle_id, "timestamp": timestamp})

        # Update vehicle count based on vehicle list size
        aggregated_data[location]["vehicle_count"] = len(aggregated_data[location]["vehicles"])
    traffic_data.clear()
    
    # Print the aggregated data
    print_aggregated_data()
    aggregated_data.clear()

# Function to print aggregated data
def print_aggregated_data():
    print("\n🔹 Aggregated Data 🔹")
    for location, data in aggregated_data.items():
        print(f"Location: {location}")
        print(f"  Status: {data['status']}")
        print(f"  Vehicle Count: {data['vehicle_count']}")
        print(f"  Vehicles with Timestamps: {data['vehicles']}")
        print("-" * 40)
