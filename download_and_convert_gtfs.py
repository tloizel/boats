import requests
import zipfile
import os
import pandas as pd

# URL for the GTFS zip file
url = 'http://nycferry.connexionz.net/rtt/public/utility/gtfs.aspx'
zip_file_path = 'gtfs_data.zip'

# Download the GTFS zip file
response = requests.get(url)

with open(zip_file_path, 'wb') as f:
    f.write(response.content)

# Extract the files from the zip archive
extract_folder = 'gtfs_files'
if not os.path.exists(extract_folder):
    os.makedirs(extract_folder)

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_folder)

# Convert each GTFS file into JSON
for file_name in os.listdir(extract_folder):
    file_path = os.path.join(extract_folder, file_name)
    if file_name.endswith('.txt'):  # Only process text files (GTFS files)
        df = pd.read_csv(file_path)
        json_data = df.to_json(orient='records', lines=True)  # Convert to JSON

        # Write to a JSON file
        json_file_name = f'{file_name.replace(".txt", ".json")}'
        with open(f'{extract_folder}/{json_file_name}', 'w') as json_file:
            json_file.write(json_data)
