import pandas as pd
import os
import requests
import zipfile
import shutil

# Constants for paths and URLs
GTFS_URL = 'http://nycferry.connexionz.net/rtt/public/utility/gtfs.aspx'
ZIP_FILE_PATH = 'gtfs_data.zip'
EXTRACT_FOLDER = 'gtfs_files'
OUTPUT_FOLDER = 'gtfs_json_split'
METADATA_FOLDER = 'gtfs_json_metadata'


def download_gtfs(url, zip_path):
    """Download the GTFS zip file."""
    print("Downloading GTFS zip file...")
    response = requests.get(url)
    with open(zip_path, 'wb') as f:
        f.write(response.content)
    print("Download complete.")


def extract_zip(zip_path, extract_folder):
    """Extract the GTFS zip file."""
    print("Extracting GTFS zip file...")
    if os.path.exists(extract_folder):
        shutil.rmtree(extract_folder)
    os.makedirs(extract_folder)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)
    print("Extraction complete.")


def load_dataframes(extract_folder):
    """Load GTFS files into pandas DataFrames."""
    print("Loading GTFS files into DataFrames...")
    routes_df = pd.read_csv(os.path.join(extract_folder, 'routes.txt'))
    calendar_df = pd.read_csv(os.path.join(extract_folder, 'calendar.txt'))
    stop_times_df = pd.read_csv(os.path.join(extract_folder, 'stop_times.txt'))
    stops_df = pd.read_csv(os.path.join(extract_folder, 'stops.txt'))
    trips_df = pd.read_csv(os.path.join(extract_folder, 'trips.txt'))
    print("DataFrames loaded successfully.")
    return routes_df, calendar_df, stop_times_df, stops_df, trips_df


def create_hierarchical_json(final_df, output_folder):
    """Create hierarchical folder structure and save JSON files."""
    print("Creating hierarchical JSON files...")
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)

    hierarchical_df = final_df[['route_id', 'service_id', 'direction_id', 'stop_id', 'trip_id', 'arrival_time']]

    for route_id in hierarchical_df['route_id'].unique():
        route_folder = os.path.join(output_folder, route_id)
        os.makedirs(route_folder, exist_ok=True)

        route_df = hierarchical_df[hierarchical_df['route_id'] == route_id]

        for service_id in route_df['service_id'].unique():
            service_folder = os.path.join(route_folder, str(service_id))
            os.makedirs(service_folder, exist_ok=True)

            service_df = route_df[route_df['service_id'] == service_id]

            for direction_id in service_df['direction_id'].unique():
                direction_folder = os.path.join(service_folder, str(direction_id))
                os.makedirs(direction_folder, exist_ok=True)

                direction_df = service_df[service_df['direction_id'] == direction_id]

                for stop_id in direction_df['stop_id'].unique():
                    stop_folder = os.path.join(direction_folder, str(stop_id))
                    os.makedirs(stop_folder, exist_ok=True)

                    stop_df = direction_df[direction_df['stop_id'] == stop_id]

                    # Keep only trip_id and arrival_time for the final JSON
                    final_json_df = stop_df[['trip_id', 'arrival_time']]

                    # Save the JSON file in the lowest-level folder
                    json_file_path = os.path.join(stop_folder, 'data.json')
                    final_json_df.to_json(json_file_path, orient='records', indent=4)
    print(f"Hierarchical JSON files created in '{output_folder}' folder.")


def create_metadata_file(final_df, stops_df, metadata_folder):
    """Create hierarchical metadata file."""
    print("Creating hierarchical metadata file...")
    
    # Merge stops with the final DataFrame to include stop_name
    metadata_df = final_df.merge(stops_df[['stop_id', 'stop_name']], on='stop_id', how='inner')
    metadata_df = metadata_df[['route_id', 'route_long_name', 'stop_id', 'stop_name', 'trip_headsign', 'direction_id']].drop_duplicates()

    # Create hierarchical structure
    hierarchical_data = {"routes": []}

    for route_id, route_group in metadata_df.groupby('route_id'):
        route_long_name = route_group['route_long_name'].iloc[0]
        route_data = {"route_id": route_id, "route_long_name": route_long_name, "stops": []}

        for stop_id, stop_group in route_group.groupby('stop_id'):
            stop_name = stop_group['stop_name'].iloc[0]
            stop_data = {"stop_id": stop_id, "stop_name": stop_name, "headsigns": []}

            for _, headsign_row in stop_group.iterrows():
                headsign_data = {
                    "trip_headsign": headsign_row['trip_headsign'],
                    "direction_id": headsign_row['direction_id']
                }
                stop_data["headsigns"].append(headsign_data)

            route_data["stops"].append(stop_data)

        hierarchical_data["routes"].append(route_data)

    # Create metadata folder
    if os.path.exists(metadata_folder):
        shutil.rmtree(metadata_folder)
    os.makedirs(metadata_folder)

    # Save the hierarchical metadata file
    metadata_file_path = os.path.join(metadata_folder, 'metadata.json')
    with open(metadata_file_path, 'w') as f:
        json.dump(hierarchical_data, f, indent=4)

    print(f"Metadata file created in '{metadata_folder}' folder.")


def main():
    """Main function to orchestrate the process."""
    # Step 1: Download the GTFS zip file
    download_gtfs(GTFS_URL, ZIP_FILE_PATH)

    # Step 2: Extract the GTFS zip file
    extract_zip(ZIP_FILE_PATH, EXTRACT_FOLDER)

    # Step 3: Load GTFS files into pandas DataFrames
    routes_df, calendar_df, stop_times_df, stops_df, trips_df = load_dataframes(EXTRACT_FOLDER)

    # Step 4: Merge DataFrames to build the final table
    trips_routes_df = pd.merge(trips_df, routes_df, on='route_id', how='inner')
    stop_times_trips_routes_df = pd.merge(stop_times_df, trips_routes_df, on='trip_id', how='inner')
    final_df = stop_times_trips_routes_df.merge(calendar_df[['service_id']], on='service_id', how='inner')

    # Step 5: Create hierarchical JSON files
    create_hierarchical_json(final_df, OUTPUT_FOLDER)

    # Step 6: Create metadata file
    create_metadata_file(final_df, stops_df, METADATA_FOLDER)


if __name__ == "__main__":
    main()
