import json
import requests
from datetime import datetime

# Base URL for the raw files in the GitHub repository
GTFS_SPLIT_FOLDER = "https://raw.githubusercontent.com/tloizel/boats_json/main/gtfs_json_split"

def build_json_url(route_id, service_id, direction_id, stop_id):
    """
    Build the URL to the JSON file based on route_id, service_id, direction_id, and stop_id.
    """
    return f"{GTFS_SPLIT_FOLDER}/{route_id}/{service_id}/{direction_id}/{stop_id}/data.json"

def get_next_ferry(route_id, service_id, direction_id, stop_id):
    """
    Retrieve the next ferry time based on the current time.
    """
    try:
        # Build the URL to the JSON file
        json_url = build_json_url(route_id, service_id, direction_id, stop_id)

        # Fetch the JSON file from the URL
        response = requests.get(json_url)
        if response.status_code != 200:
            print(f"JSON file not found at: {json_url}")
            return None

        ferry_data = response.json()

        # Get the current time
        current_time = datetime.now().time()

        # Find the next ferry (arrival_time > current_time)
        for ferry in ferry_data:
            ferry_time = datetime.strptime(ferry["arrival_time"], "%H:%M:%S").time()
            if ferry_time > current_time:
                return ferry_time

        print("No more ferries available for today.")
        return None

    except Exception as e:
        print(f"Error retrieving next ferry: {e}")
        return None

def main():
    """
    Main function to demonstrate functionality.
    """
    # Example inputs (update these as needed)
    route_id = "AS"  # Route ID
    service_id = 1  # Service ID
    direction_id = 0  # Direction ID
    stop_id = 87  # Stop ID

    # Retrieve the next ferry time
    next_ferry = get_next_ferry(route_id, service_id, direction_id, stop_id)

    # Print the result
    if next_ferry:
        print(f"The next ferry for Route ID '{route_id}', Service ID '{service_id}', Direction ID '{direction_id}', Stop ID '{stop_id}' is at {next_ferry}.")
    else:
        print("No next ferry found.")

if __name__ == "__main__":
    main()
    
