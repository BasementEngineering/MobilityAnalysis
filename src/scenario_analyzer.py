from time import time
import requests
import datetime
import os
import pprint
import json
from dotenv import load_dotenv

# Set your Google Maps API key here or use an environment variable
load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
#API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "YOUR_API_KEY_HERE")

ORIGIN = "Dompl. 28, 48143 Münster"
DESTINATION = "Albersloher Weg 14, 48155 Münster"
ARRIVAL_TIME = datetime.datetime(2025, 9, 27, 18, 0)  # 26th Sep 2024, 18:00

# Convert arrival time to Unix timestamp
arrival_time_unix = int(ARRIVAL_TIME.timestamp())

MODES = {
    "driving": "Car",
    "bicycling": "Bike",
    "walking": "Foot",
    "transit": "Transit"
}

def get_travel_time(mode):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": ORIGIN,
        "destination": DESTINATION,
        "mode": mode,
        "arrival_time": arrival_time_unix,
        "key": API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    #print()
    #pprint.pprint(data)  # Debug: pretty-print the full response data
    # Write the response JSON to a file for each mode
    output_filename = f"maps_response_{mode}.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    if data["status"] == "OK":
        route = data["routes"][0]["legs"][0]
        duration = route["duration"]["text"]
        return duration
    else:
        return f"Error: {data.get('status', 'Unknown error')}"

def newFileInInputFolder():
    input_folder = os.path.join(os.path.dirname(__file__), "input")
    files = os.listdir(input_folder)
    return any(file.endswith(".json") for file in files)

def getLastFileInInputFolder():
    input_folder = os.path.join(os.path.dirname(__file__), "input")
    files = [file for file in os.listdir(input_folder) if file.endswith(".json")]
    if not files:
        return None
    files.sort(key=lambda x: os.path.getmtime(os.path.join(input_folder, x)), reverse=True)
    return files[0]

def get_trips_from_data(profile):
    for daily_routine in profile.get("daily_routines", []):
        origin = daily_routine.get("origin")
        destination = daily_routine.get("destination")
        mode = daily_routine.get("mode", "driving")
        if origin and destination:
            yield origin, destination, mode

def main():
    print("Starting scenario analyzer...")
    for _ in range(3):
        while not newFileInInputFolder():
            time.sleep(1)
        filename = getLastFileInInputFolder()
        if filename:
            print(f"Processing file: {filename}")
            filepath = os.path.join(os.path.dirname(__file__), "input", filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"Loaded data: {data}")
        else:
            print("No input file found.")
            return
        
        trips = get_trips_from_data(data)
        for daily_routine in data.get("daily_routines", []):
            origin = daily_routine.get("origin")
            destination = daily_routine.get("destination")
            mode = daily_routine.get("mode", "driving")
            if origin and destination:
                print(f"Analyzing trip from {origin} to {destination} by {MODES.get(mode, mode)}")
                travel_time = get_travel_time(mode)
                print(f"Estimated travel time by {MODES.get(mode, mode)}: {travel_time}")
                daily_routine["estimated_travel_time"] = travel_time


       # print(f"Estimated travel time by {MODES[mode]}: {travel_time}")



if __name__ == "__main__":
    main()