from pymongo import MongoClient
import logging
import os
from dotenv import load_dotenv
import ssl
import time

load_dotenv()  # Load MongoDB URI from .env

# MongoDB Atlas connection
# MongoDB Atlas connection
client = MongoClient(os.getenv("MONGO_URI"))  # This gives you the client
db = client["traffic_monitoring"]             # Now you access your database

critical_events_col = db["critical_events"]                   # Now this is correct
aggregated_traffic_col = db["normal_events_aggregated"]

logging.info("Mongo DB Cloud Connected Successfully...")

def stringify_keys(d):
    return {str(k): v for k, v in d.items()}

def log_critical_event(event):
    try:
        critical_events_col.insert_one(event)
        logging.info("✅ Logged critical event to MongoDB cloud.")
    except Exception as e:
        logging.error(f"❌ Failed to log critical event: {e}")

def format_aggregated_data(aggregated_data):
    """
    Converts defaultdict with tuple keys into MongoDB-acceptable dict:
    - Tuple keys -> String keys
    - Adds timestamp
    """
    formatted = {}
    for key, value in aggregated_data.items():
        # Convert tuple keys like (0, -1) to string "(0,-1)"
        formatted[str(key)] = value

    return {
        "aggregated_timestamp": int(time.time()),
        "data": formatted
    }

def log_aggregated_data(aggregated_data):
    try:
        # Format aggregated data into MongoDB-compatible format
        doc = format_aggregated_data(aggregated_data)
        
        # Insert the document into the MongoDB collection
        aggregated_traffic_col.insert_one(doc)
        logging.info("✅ Logged aggregated data to MongoDB cloud.")
    except Exception as e:
        logging.error(f"❌ Failed to log aggregated data: {e}")
