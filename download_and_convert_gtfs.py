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
json_folder = 'gtfs_json'

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

# Filter columns to keep only the required attributes
final_df = final_df[['route_id', 'service_id', 'stop_id', 'direction_id', 'trip_id', 'trip_headsign', 'arrival_time']]

# Step 5: Save the final merged table as a JSON file
if os.path.exists(json_folder):
    shutil.rmtree(json_folder)
os.makedirs(json_folder)

final_json_path = os.path.join(json_folder, 'merged_data.json')
final_df.to_json(final_json_path, orient='records', indent=4)

print(f"Successfully created merged JSON file: {final_json_path}")
