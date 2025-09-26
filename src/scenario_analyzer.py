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

def main():
    print(f"Directions from {ORIGIN} to {DESTINATION} (arrival at {ARRIVAL_TIME.strftime('%H:%M')})")
    for mode, label in MODES.items():
        travel_time = get_travel_time(mode)
        print(f"{label}: {travel_time}")

if __name__ == "__main__":
    main()