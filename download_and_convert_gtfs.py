import requests
import zipfile
import os
import shutil  # Import shutil to delete the folder
import pandas as pd

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
# Delete the extract folder if it already exists (clean slate)
if os.path.exists(extract_folder):
    shutil.rmtree(extract_folder)

os.makedirs(extract_folder)  # Create a new, empty folder

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_folder)  # Extract all files into the clean folder

# Step 3: Convert specific files to JSON
# Delete the JSON folder if it already exists (clean slate)
if os.path.exists(json_folder):
    shutil.rmtree(json_folder)

os.makedirs(json_folder)  # Create a new, empty folder

# List of files to convert to JSON
files_to_convert = ['routes.txt', 'calendar.txt', 'stops.txt']

for file_name in files_to_convert:
    file_path = os.path.join(extract_folder, file_name)
    if os.path.exists(file_path):  # Check if the file exists
        df = pd.read_csv(file_path)
        json_data = df.to_json(orient='records')  # Convert to JSON array format

        # Write to a JSON file in the gtfs_json folder
        json_file_name = file_name.replace('.txt', '.json')
        with open(os.path.join(json_folder, json_file_name), 'w') as json_file:
            json_file.write(json_data)
        print(f"Converted {file_name} to {json_file_name}")
    else:
        print(f"{file_name} not found in the GTFS archive.")

print(f"GTFS files successfully downloaded, extracted, and converted to JSON in '{json_folder}' folder.")
