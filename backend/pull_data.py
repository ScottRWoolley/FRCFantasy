import requests
import json
import os

def event(team_key, event_key):
    file_path = f"data/{team_key}/{event_key}.json"

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Read API key
    with open("api_key.txt", "r") as file:
        api_key = file.read().strip()

    headers = {'X-TBA-Auth-Key': api_key}

    # Get data from API
    url = f"https://www.thebluealliance.com/api/v3/team/{team_key}/event/{event_key}/matches"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        json_data = response.json()

        # Write response directly to JSON file (overwrite)
        with open(file_path, "w") as f:
            json.dump(json_data, f, indent=4)

        #print(f"Data saved to {file_path}")
    else:
        print(f"Error {response.status_code}: {response.text}")

