# **Boats ⛵️**

Welcome to the **Boats JSON Project**, a repository for processing, organizing, and retrieving GTFS (General Transit Feed Specification) data from NYC Ferry services. This project automates the downloading, parsing, and hierarchical organization of GTFS data into JSON files, making it easy to query and configure transit-related information.

---

### **`.github/workflows/`**

- **`gtfs-download.yml`**:A GitHub Actions workflow that executes the **download_and_convert_gtfs.py** script to automate the downloading, parsing, and organizing of GTFS data into JSON files.

### **`gtfs_files/`**

- Contains the raw GTFS **.txt** files extracted from the downloaded GTFS zip file:
    - **agency.txt**: Transit agency details.
    - **calendar.txt**: Service schedules.
    - **calendar_dates.txt**: Exceptions to service schedules.
    - **fare_attributes.txt**: Fare-related details.
    - **feed_info.txt**: Metadata about the GTFS feed.
    - **routes.txt**: Route information (e.g., route IDs and names).
    - **shapes.txt**: Shape information for routes.
    - **stop_times.txt**: Stop times for trips.
    - **stops.txt**: Stop details (e.g., stop IDs and names).
    - **trips.txt**: Trip details (e.g., trip IDs and route associations).

### **`gtfs_json_metadata/`**

- **`metadata.json`**:A hierarchical JSON file containing information about routes, stops, trip headsigns, and direction IDs. This file is structured for easy querying.

### **`gtfs_json_split/`**

- Contains subfolders organized by route IDs. Each folder contains nested subfolders based on service IDs, direction IDs, and stop IDs. At the lowest level, each folder contains a **data.json** file with trip IDs and arrival times for the specific route, service, direction, and stop.

### **`Root Files`**

- **`download_and_convert_gtfs.py`**:The main Python script executed by the GitHub Actions workflow (**gtfs-download.yml**). It automates the downloading, parsing, and hierarchical organization of GTFS data into JSON files.
- **gtfs_data.zip**:The raw GTFS zip file downloaded from NYC Ferry services.

### **`local_scripts/`**

- **`retrieve_metadata.py`**:A Python script for querying the **metadata.json** file. It allows you to:
    - Retrieve all route IDs and their long names.
    - Retrieve all stop IDs and stop names for a specific route ID.
    - Retrieve trip headsigns and direction IDs for a specific route ID and stop ID.
