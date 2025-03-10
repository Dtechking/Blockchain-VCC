import json
import threading

def aggregate_data(traffic_data_storage):
    """Aggregates verified traffic data into meaningful insights"""
    aggregated_data = {
        "congested_areas": [],
        "accident_spots": [],
        "free_flow_zones": []
    }

    # Aggregate traffic data
    for entry in traffic_data_storage:
        location = entry['location']
        status = entry['traffic_status']

        if status == "Congested":
            aggregated_data['congested_areas'].append(location)
        elif status == "Accident Detected":
            aggregated_data['accident_spots'].append(location)
        else:
            aggregated_data['free_flow_zones'].append(location)

    # Simulate sending data to blockchain
    print(f"🚦 Aggregated Traffic Data:\n{json.dumps(aggregated_data, indent=2)}")

    # Clear buffer after aggregation
    traffic_data_storage.clear()
