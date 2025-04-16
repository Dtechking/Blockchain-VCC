from collections import defaultdict
import time
import json
import os

# Local cache file path
DATA_CACHE_FILE = "cache/aggregated_traffic_cache.json"
CACHE_TTL_SECONDS = 5 * 60  # 5 minutes

# Aggregated data structure
aggregated_data = defaultdict(lambda: {
    "status": None,
    "vehicle_count": 0,
    "vehicles": []  # List of {"vehicle_id", "timestamp"}
})

traffic_data = []

# Load cache from local file (if exists and not expired)
def load_cache(DATA_CACHE_FILE):
    if not os.path.exists(DATA_CACHE_FILE):
        # Create an empty cache file with current timestamp
        with open(DATA_CACHE_FILE, "w") as f:
            json.dump({
                "timestamp": time.time(),
                "data": {}
            }, f, indent=4)
        print("📁 Cache file not found. Created new cache file.\n")
        return

    with open(DATA_CACHE_FILE, "r") as f:
        try:
            cached = json.load(f)
            cache_time = cached.get("timestamp", 0)
            current_time = time.time()

            if current_time - cache_time > CACHE_TTL_SECONDS:
                print("⚠️ Cache expired. Ignoring old data.\n")
                return

            raw_data = cached.get("data", {})
            for loc_str, data in raw_data.items():
                loc_tuple = tuple(loc_str.strip("()").split(", "))
                aggregated_data[loc_tuple] = data
            print("✅ Cache loaded successfully.\n")
        except Exception as e:
            print(f"⚠️ Failed to load cache: {e}\n")

# Save cache to local file
def save_cache(DATA_CACHE_FILE):
    with open(DATA_CACHE_FILE, "w") as f:
        serializable_data = {str(k): v for k, v in aggregated_data.items()}
        json.dump({
            "timestamp": time.time(),
            "data": serializable_data
        }, f, indent=4)
    print("💾 Aggregated data saved to cache.\n")

# Add data to aggregation
def aggregate_data(traffic_data_storage):
    aggregated_data.clear()
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
                vehicle["timestamp"] = vehicle["timestamp"]
                break
        else:
            # Add new vehicle entry if not found
            aggregated_data[location]["vehicles"].append({"vehicle_id": vehicle_id, "timestamp": timestamp})

        # Update vehicle count based on vehicle list size
        aggregated_data[location]["vehicle_count"] = len(aggregated_data[location]["vehicles"])
    traffic_data.clear()
    
    # Print the aggregated data
    print_aggregated_data()
    save_cache(DATA_CACHE_FILE)  # Save data after aggregation
    return aggregated_data

# Function to print aggregated data
def print_aggregated_data():
    print("\n\n🔹 Aggregated Data 🔹")
    for location, data in aggregated_data.items():
        print(f"Location: {location}")
        print(f"  Status: {data['status']}")
        print(f"  Vehicle Count: {data['vehicle_count']}")
        print(f"  Vehicles with Timestamps: {data['vehicles']}")
        print("-" * 40)
