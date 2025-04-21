import pandas as pd
import os
import requests
import zipfile
import shutil
import json

# URL for the GTFS zip file
url = 'http://nycferry.connexionz.net/rtt/public/utility/gtfs.aspx'
zip_file_path = 'gtfs_data.zip'

# Folder paths
extract_folder = 'gtfs_files'
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
stops_df = pd.read_csv(os.path.join(extract_folder, 'stops.txt'))
trips_df = pd.read_csv(os.path.join(extract_folder, 'trips.txt'))
stop_times_df = pd.read_csv(os.path.join(extract_folder, 'stop_times.txt'))

# Rename stop_code to stop_id if necessary
if 'stop_code' in stops_df.columns:
    stops_df.rename(columns={'stop_code': 'stop_id'}, inplace=True)

# Step 4: Merge DataFrames to build the final table
# Merge stop_times with trips to associate stop_id with trip_id
stop_times_trips_df = pd.merge(stop_times_df, trips_df, on='trip_id', how='inner')

# Merge the result with routes to include route_id and route_long_name
stop_times_trips_routes_df = pd.merge(stop_times_trips_df, routes_df, on='route_id', how='inner')

# Merge the result with stops to include stop_name
final_df = pd.merge(stop_times_trips_routes_df, stops_df, on='stop_id', how='inner')

# Filter columns for metadata
metadata_df = final_df[['route_id', 'route_long_name', 'stop_id', 'stop_name', 'trip_headsign', 'direction_id']]

# Step 5: Create hierarchical JSON structure
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

# Step 6: Save hierarchical JSON to metadata folder
if os.path.exists(metadata_folder):
    shutil.rmtree(metadata_folder)
os.makedirs(metadata_folder)

metadata_file_path = os.path.join(metadata_folder, 'metadata.json')
with open(metadata_file_path, 'w') as f:
    json.dump(hierarchical_data, f, indent=4)

print(f"Successfully created metadata file in '{metadata_folder}' folder.")
