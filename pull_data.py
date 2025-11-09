import requests
import json
# pip install statbotics==2.0.1
import os
import json
import requests

def pull_matches(event_key):
    file_path = f"data/matches/{event_key}.json"
    
    # Load API key
    with open("api_key.txt", "r") as file:
        api_key = file.read().strip()
    headers = {'X-TBA-Auth-Key': api_key}
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Make request to TBA
    url = f"https://www.thebluealliance.com/api/v3/event/{event_key}/matches/simple"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        json_data = response.json()
        
        # Load existing file if it exists
        if os.path.isfile(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
        else:
            data = {}

        # Add matches
        data['matches'] = json_data

        # Save to file
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Saved {len(json_data)} matches to {file_path}")
    else:
        print(f"Error {response.status_code}: {response.text}")


def pull_comps(year):
    import os, json, requests
    
    page_num = 0
    file_path = "data/comps.json"
    with open("api_key.txt", "r") as file:
        api_key = file.read().strip()
    headers = {'X-TBA-Auth-Key': api_key}
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Create the file if it does not exist yet
    if not os.path.isfile(file_path):
        with open(file_path, "w") as f:
            json.dump({"comps": []}, f, indent=4)

    url = f"https://www.thebluealliance.com/api/v3/events/{year}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        json_data = response.json()

        # pick only the fields you want from each event
        filtered_events = []
        for event in json_data:
            if event.get("event_type") == 0:
                filtered_events.append({
                    "key": event.get("key"),
                    "name": event.get("name"),
                    "event_code": event.get("event_code"),
                    "event_type": event.get("event_type"),
                    "start_date": event.get("start_date"),
                    "end_date": event.get("end_date"),
                    "week": event.get("week"),
                    "country": event.get("country")
                })

        with open(file_path, "r") as f:
            data = json.load(f)
        if "comps" not in data:
            data["comps"] = []
        data["comps"].extend(filtered_events)

        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)


def pull_year(year):
    page_num = 0
    page = True
    file_path = "data/teams.json"
    with open("api_key.txt", "r") as file:
        api_key = file.read()
    headers = { 'X-TBA-Auth-Key': api_key }
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Create the file if it does not exist yet
    if not os.path.isfile(file_path):
        with open(file_path, "w") as f:
            json.dump({}, f, indent=4)

    while page:
        print(page_num)
        url = f"https://www.thebluealliance.com/api/v3/teams/{year}/{page_num}/simple"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            json_data = response.json()
            if len(json_data) < 1:
                page = False
            with open(file_path, "r") as f:
                data = json.load(f)
            if 'teams' not in data:
                data['teams'] = []
            data['teams'].extend(json_data)

            with open(file_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)

            page_num += 1
def pull_epa(year):
    with open('data/teams.json', 'r') as file:
        data = json.load(file)

    keys = [int(team['key'][3:]) for team in data['teams']]

    sb = statbotics.Statbotics()

    all_team_data = []

    for key in keys:
        try:
            team_data = sb.get_team_year(key,year)
            print(team_data)
            all_team_data.append(team_data)
        except UserWarning as e:
            print(f"Warning for team {key}: {e}")
        except Exception as e:
            # catch other unexpected errors
            print(f"Error for team {key}: {e}")

    with open("data/statbotics_data.json", "w") as json_file:
        json.dump(all_team_data, json_file, indent=4)