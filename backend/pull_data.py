import json
import os
import time
from backend import scoring


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
    eventtime = 0
    file_path = f"data/{team_key}/{event_key}.json"

    # Make sure folder exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Check if file exists before reading
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
                # Example: print the first actual_time value
                if data and "actual_time" in data[0 ]:
                    eventtime = data[0]["actual_time"]
                else:
                    print("it really fo me real")
            except json.JSONDecodeError:
                print("it be real")
    current_time = int(time.time())
    if current_time <= eventtime or eventtime == 0:
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
        return 0
    else:
        return 1



def read_events(file_path):
    with open(file_path, 'r') as f:
        events = json.load(f)
    return events

def pull_teams(team_list):
    year = "2025"
    team_scores = {}

    with open("data/scores.json", "r") as f:
        data = json.load(f)

    for team in team_list:
        find_events(team, year)
        events_data = read_events(f"data/{team}/{year}.json")
        team_score = 0
        for e in events_data:
            if e['event_type'] == 0:
                repeat = event(team, e['key'])
                print(repeat)
                team_score += scoring.calculate_team_scores(team, e['key'])
        team_scores[team] = team_score
    return team_scores




