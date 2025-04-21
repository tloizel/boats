import pandas as pd
import os
import requests
import zipfile
import shutil

# URL for the GTFS zip file
url = 'http://nycferry.connexionz.net/rtt/public/utility/gtfs.aspx'
zip_file_path = 'gtfs_data.zip'

# Folder paths
extract_folder = 'gtfs_files'
output_folder = 'gtfs_json_split'
metadata_folder = 'gtfs_json_metadata'

# Step 1: Download the GTFS zip file
response = requests.get(url)
with open(zip_file_path, 'wb') as f:
    f.write(response.content)

# Step 2: Extract the files from the zip archive
if os.path.exists(extract_folder):
    shutil.rmtree(extract_folder)
os.makedirs(extract_folder)

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_folder)

# Step 3: Load GTFS files into pandas DataFrames
routes_df = pd.read_csv(os.path.join(extract_folder, 'routes.txt'))
calendar_df = pd.read_csv(os.path.join(extract_folder, 'calendar.txt'))
stop_times_df = pd.read_csv(os.path.join(extract_folder, 'stop_times.txt'))
stops_df = pd.read_csv(os.path.join(extract_folder, 'stops.txt'))
trips_df = pd.read_csv(os.path.join(extract_folder, 'trips.txt'))

# Step 4: Merge DataFrames to build the final table
# Merge trips with routes to get route_id and trip details
trips_routes_df = pd.merge(trips_df, routes_df, on='route_id', how='inner')

# Merge stop_times with trips_routes to add arrival_time and stop_id
stop_times_trips_routes_df = pd.merge(stop_times_df, trips_routes_df, on='trip_id', how='inner')

# Add service_id from calendar (optional: filter based on service_id if needed)
final_df = stop_times_trips_routes_df.merge(calendar_df[['service_id']], on='service_id', how='inner')

# Filter columns to keep only the required attributes for hierarchical JSON files
hierarchical_df = final_df[['route_id', 'service_id', 'direction_id', 'stop_id', 'trip_id', 'arrival_time']]

# Step 5: Create hierarchical folder structure and split JSONs
if os.path.exists(output_folder):
    shutil.rmtree(output_folder)
os.makedirs(output_folder)

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

# Step 6: Create metadata file
# Merge stops and routes to include stop_name and route_long_name
metadata_df = final_df.merge(stops_df[['stop_id', 'stop_name']], on='stop_id', how='inner')
metadata_df = metadata_df[['route_id', 'route_long_name', 'stop_id', 'stop_name', 'trip_headsign', 'direction_id']].drop_duplicates()

# Create metadata folder
if os.path.exists(metadata_folder):
    shutil.rmtree(metadata_folder)
os.makedirs(metadata_folder)

# Save the metadata file
metadata_file_path = os.path.join(metadata_folder, 'metadata.json')
metadata_df.to_json(metadata_file_path, orient='records', indent=4)

print(f"Successfully created hierarchical JSON files in '{output_folder}' folder.")
print(f"Successfully created metadata file in '{metadata_folder}' folder.")
