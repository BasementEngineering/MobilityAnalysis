import os
from dotenv import load_dotenv
import requests
import json
import random

profile_id = "user_12345"

data_structure = {
    "daily_routines": [
        {
            "time": "07:00",
            "activity": "Wake up",
            "location": "home"
        },
        {
            "time": "09:00",
            "activity": "Work",
            "location": "office"
        },
        {
            "time": "18:00",
            "activity": "Gym",
            "location": "gym"
        },
        {
            "time": "20:00",
            "activity": "Return home",
            "location": "home"
        }
    ]
}

def get_unique_locations(data):
    return list(set(item["location"] for item in data["daily_routines"]))

def find_closest_location(query, start_location, api_key):
    print(f"Finding closest location for query: {query}")
    # Use the newer Google Places API: Text Search
    endpoint = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    params = {
        "query": query,
        "location": f"{start_location[0]},{start_location[1]}",
        "radius": 5000,  # meters
        "key": api_key
    }

    response = requests.get(endpoint, params=params)
    print("Response Status Code:", response.status_code)
    timestamp = int(os.times()[4])
    filename = f"debug_{query}_{timestamp}.json"
    print(f"Saving debug info to {filename}")
    save_debug(response.json(), filename)
    results = response.json().get("results", [])

    if results:
        random_index = random.randint(0, min(2, len(results) - 1))  # Pick a random index among the first three results if available
        return results[random_index].get("geometry", {}).get("location", {})
    else:
        print(f"No results found for query: {query}")
    return None

#For file output
def save_output(data, filename):
    import json

    # Transform data to GeoJSON FeatureCollection
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        item["coordinates"]["lng"],
                        item["coordinates"]["lat"]
                    ]
                },
                "properties": {
                    "name": item["name"]
                }
            }
            for item in data if item["coordinates"]
        ]
    }
    data = geojson


    output_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    os.makedirs(output_folder, exist_ok=True)
    filepath = os.path.join(output_folder, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def save_debug(data, filename):
    debug_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "debug")
    os.makedirs(debug_folder, exist_ok=True)
    filepath = os.path.join(debug_folder, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# main
if __name__ == "__main__":
    print("Generating points of interest based on daily routines...")
    load_dotenv()
    API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

    home_location = [51.9607, 7.6261]  # Example: Münster, Germany

    print("Using Google Maps API Key:", "" + ("Set" if API_KEY else "Not Set"))
    api_key = API_KEY

    unique_locations = get_unique_locations(data_structure)
    print("Unique locations found:", unique_locations)
    closest_locations = {}

    closest_locations["home"] = {"lat": home_location[0], "lng": home_location[1]}

    for loc in unique_locations:
        if loc == "home":
            continue
        coordinates = find_closest_location(loc, home_location, api_key)
        closest_locations[loc] = coordinates

    print(closest_locations)

    points_of_interest = [
        {
            "name": loc,
            "coordinates": closest_locations[loc]
        }
        for loc in unique_locations
    ]

    save_output(points_of_interest, "points_of_interest.json")

    profile = {
        "daily_routines": data_structure["daily_routines"],
        "points_of_interest": points_of_interest
    }

    save_output(profile, f"{profile_id}_user_profile.json")