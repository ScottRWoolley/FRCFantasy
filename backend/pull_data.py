import requests
import json
import os

def find_events(team_key, year):
    file_path = f"data/{team_key}/{year}.json"

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open("api_key.txt", "r") as file:
        api_key = file.read().strip()

    headers = {'X-TBA-Auth-Key': api_key}

    url = f"https://www.thebluealliance.com/api/v3/team/{team_key}/events/{year}/simple"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        json_data = response.json()

        with open(file_path, "w") as f:
            json.dump(json_data, f, indent=4)

    else:
        print(f"Error {response.status_code}: {response.text}")

def event(team_key, event_key):
    file_path = f"data/{team_key}/{event_key}.json"

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open("api_key.txt", "r") as file:
        api_key = file.read().strip()

    headers = {'X-TBA-Auth-Key': api_key}

    url = f"https://www.thebluealliance.com/api/v3/team/{team_key}/event/{event_key}/matches"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        json_data = response.json()

        with open(file_path, "w") as f:
            json.dump(json_data, f, indent=4)

    else:
        print(f"Error {response.status_code}: {response.text}")

def read_events(file_path):
    with open(file_path, 'r') as f:
        events = json.load(f)
    return events

def pull_teams(team_list):
    year = "2025"

    for team in team_list:
        find_events(team, year)
        events_data = read_events(f"data/{team}/{year}.json")
        for e in events_data:
            if e['event_type'] == 0:
                event(team, e['key'])




