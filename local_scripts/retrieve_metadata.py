import json
import requests

# URL to the raw metadata.json file on GitHub
METADATA_URL = "https://raw.githubusercontent.com/tloizel/boats_json/main/gtfs_json_metadata/metadata.json"

def fetch_metadata(url):
    """Fetch the metadata JSON file from the provided URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad HTTP responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the metadata file: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the URL: {url}")
        return None

def get_routes(metadata):
    """Retrieve route IDs and their long names from the metadata."""
    try:
        routes = [(route["route_id"], route["route_long_name"]) for route in metadata["routes"]]
        return routes
    except KeyError:
        print("Error: Invalid metadata format.")
        return []

def get_stops_for_route(route_id, metadata):
    """Retrieve stop IDs and stop names for a given route ID."""
    try:
        for route in metadata["routes"]:
            if route["route_id"] == route_id:
                stops = [(stop["stop_id"], stop["stop_name"]) for stop in route["stops"]]
                return stops
        print(f"No route found with ID: {route_id}")
        return []
    except KeyError:
        print("Error: Invalid metadata format.")
        return []

def get_headsigns_for_route_and_stop(route_id, stop_id, metadata):
    """Retrieve trip_headsigns and direction IDs for a given route ID and stop ID."""
    try:
        for route in metadata["routes"]:
            if route["route_id"] == route_id:
                for stop in route["stops"]:
                    if stop["stop_id"] == stop_id:
                        headsigns = [(headsign["trip_headsign"], headsign["direction_id"]) for headsign in stop["headsigns"]]
                        return headsigns
                print(f"No stop found with ID: {stop_id} for Route ID: {route_id}")
                return []
        print(f"No route found with ID: {route_id}")
        return []
    except KeyError:
        print("Error: Invalid metadata format.")
        return []

def main():
    """Main function to demonstrate the functionality."""
    # Fetch the metadata file
    metadata = fetch_metadata(METADATA_URL)

    if metadata is None:
        print("Failed to fetch metadata. Exiting.")
        return

    # Retrieve and display all routes
    print("Route IDs and Long Names:")
    routes = get_routes(metadata)
    for route_id, route_long_name in routes:
        print(f"Route ID: {route_id}, Long Name: {route_long_name}")

    print("\n")

    # Retrieve and display stops for a specific route (default route ID: "AS")
    default_route_id = "SB"
    print(f"Stops for Route ID '{default_route_id}':")
    stops = get_stops_for_route(default_route_id, metadata)
    for stop_id, stop_name in stops:
        print(f"Stop ID: {stop_id}, Stop Name: {stop_name}")

    print("\n")

    # Retrieve and display trip_headsigns for a specific route and stop (default stop ID: 87)
    default_stop_id = 87
    print(f"Trip Headsigns for Route ID '{default_route_id}' and Stop ID '{default_stop_id}':")
    headsigns = get_headsigns_for_route_and_stop(default_route_id, default_stop_id, metadata)
    for trip_headsign, direction_id in headsigns:
        print(f"Trip Headsign: {trip_headsign}, Direction ID: {direction_id}")

if __name__ == "__main__":
    main()
